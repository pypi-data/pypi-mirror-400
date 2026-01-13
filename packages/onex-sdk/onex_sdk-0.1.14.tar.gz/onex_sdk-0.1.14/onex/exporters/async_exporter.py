"""
Async Signal Exporter
Non-blocking signal export to OneX platform
"""

import logging
import os
import queue
import threading
import time
from typing import Any, Dict, List, Optional

import requests  # type: ignore[import-not-found]

logger = logging.getLogger(__name__)


class AsyncSignalExporter:
    """
    Asynchronous signal exporter
    Exports signals and request metadata in background threads to avoid blocking inference
    """

    def __init__(
        self,
        endpoint: str,
        api_key: Optional[str] = None,
        batch_size: int = 10,
        request_payload_endpoint: Optional[str] = None,
        request_response_endpoint: Optional[str] = None,
    ):
        self.endpoint = endpoint
        self.api_key = api_key
        self.batch_size = batch_size

        self.container_id = self._detect_container_id()
        if self.container_id:
            logger.info("Signal exporter running in container %s", self.container_id)
        else:
            logger.info("Signal exporter could not detect a container identifier")

        self.request_payload_endpoint = (
            request_payload_endpoint or self._derive_related_endpoint(endpoint, "payload")
        )
        self.request_response_endpoint = (
            request_response_endpoint or self._derive_related_endpoint(endpoint, "response")
        )

        # Signal queue for async processing (thread-safe by design)
        self.signal_queue = queue.Queue(maxsize=1000)
        self.request_queue = queue.Queue(maxsize=500)

        # Thread synchronization for immediate wake-up and flush
        self._condition = threading.Condition()
        self._flush_requested = False
        self._pending_signals_count = 0

        # Start background export threads
        self.running = True
        self.export_thread = threading.Thread(target=self._export_loop, daemon=True)
        self.export_thread.start()
        self.request_thread = threading.Thread(target=self._request_export_loop, daemon=True)
        self.request_thread.start()

        logger.info("Signal exporter initialized: %s", endpoint)

    # --------------------------------------------------------------------- #
    # Signal export interface
    # --------------------------------------------------------------------- #

    def export(self, signals: Dict[str, Any]):
        """
        Export signals asynchronously.
        Non-blocking - returns immediately.
        Thread-safe - can be called concurrently from multiple threads.
        """
        try:
            payload = self._ensure_container_id(dict(signals))
            self.signal_queue.put_nowait(payload)
            
            # Wake up export thread immediately (thread-safe)
            with self._condition:
                self._pending_signals_count += 1
                self._condition.notify()  # Immediate wake-up, no timeout
        except queue.Full:
            logger.warning("Signal queue full, dropping signal")

    def export_request_payload(
        self,
        request_id: str,
        payload: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Queue a request payload event for export."""
        event = {
            "type": "payload",
            "body": self._ensure_container_id(
                self._build_request_body("payload", request_id, payload, metadata)
            ),
        }
        self._enqueue_request_event(event)

    def export_request_response(
        self,
        request_id: str,
        response_payload: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Queue a request response event for export."""
        event = {
            "type": "response",
            "body": self._ensure_container_id(
                self._build_request_body("response", request_id, response_payload, metadata)
            ),
        }
        self._enqueue_request_event(event)

    # --------------------------------------------------------------------- #
    # Background loops
    # --------------------------------------------------------------------- #

    def _export_loop(self):
        """
        Background thread that exports batches of neural signals.
        Wakes up immediately when signals arrive (no timeout delay).
        Thread-safe for concurrent signal exports.
        """
        batch: List[Dict[str, Any]] = []

        while self.running or not self.signal_queue.empty():
            try:
                # Collect all available signals immediately (handles concurrent signals)
                signals_collected = False
                flush_needed = False
                
                # Collect all signals currently in queue (non-blocking)
                while True:
                    try:
                        signal = self.signal_queue.get_nowait()
                        batch.append(self._ensure_container_id(signal))
                        signals_collected = True
                        
                        # Send immediately if batch reaches full size
                        if len(batch) >= self.batch_size:
                            self._send_batch(batch)
                            batch = []
                            
                    except queue.Empty:
                        break
                
                # Check if flush was requested (thread-safe)
                with self._condition:
                    flush_needed = self._flush_requested
                    should_send = (signals_collected or flush_needed) and batch
                    if signals_collected or flush_needed:
                        self._pending_signals_count = 0
                        if flush_needed:
                            self._flush_requested = False
                
                # Send batch if we have signals and either:
                # 1. Flush was explicitly requested, or
                # 2. We collected signals (send immediately, no delay)
                if should_send:
                    self._send_batch(batch)
                    batch = []
                elif not signals_collected:
                    # No signals available, wait for new signals or flush request
                    # This blocks until condition is notified (immediate wake-up on signal arrival)
                    with self._condition:
                        if not self.running and self.signal_queue.empty():
                            break
                        # Wait until signaled - wakes immediately when export() is called
                        # No timeout = waits indefinitely, but notify() wakes it immediately
                        self._condition.wait()
                        # After wake-up, loop immediately checks queue again
                        
            except Exception as exc:
                logger.error("Error in signal export loop: %s", exc)

        # Final flush of any remaining signals
        if batch:
            self._send_batch(batch)

    def _request_export_loop(self):
        """Background thread that exports request payloads/responses."""
        while self.running or not self.request_queue.empty():
            try:
                event = self.request_queue.get(timeout=1.0)
                event_type = event.get("type")
                body = self._ensure_container_id(event.get("body", {}))

                if event_type == "payload":
                    self._post_json(self.request_payload_endpoint, body, "request payload")
                elif event_type == "response":
                    self._post_json(self.request_response_endpoint, body, "request response")
                else:
                    logger.warning("Unknown request queue event type: %s", event_type)
            except queue.Empty:
                continue
            except Exception as exc:
                logger.error("Error exporting request data: %s", exc)

    # --------------------------------------------------------------------- #
    # HTTP helpers
    # --------------------------------------------------------------------- #

    def _send_batch(self, batch: list[Dict[str, Any]]):
        """Send batch of signals to OneX API."""
        try:
            headers: Dict[str, str] = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            sanitized_batch = [self._ensure_container_id(item) for item in batch]

            for index, payload in enumerate(sanitized_batch):
                logger.info(
                    "Preparing to export signal #%s (container_id=%s, type=%s)",
                    index,
                    payload.get("container_id"),
                    payload.get("signal_type"),
                )
                logger.info("Signal payload #%s content: %s", index, payload)

            response = requests.post(
                self.endpoint,
                json={"signals": sanitized_batch},
                headers=headers,
                timeout=5.0,
            )

            if 200 <= response.status_code < 300:
                logger.info("Exported %s signals successfully", len(batch))
            else:
                logger.warning("Signal export failed: %s", response.status_code)

        except Exception as exc:
            logger.error("Failed to export signals: %s", exc)

    def _post_json(self, endpoint: str, body: Dict[str, Any], description: str):
        try:
            headers: Dict[str, str] = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            response = requests.post(endpoint, json=body, headers=headers, timeout=5.0)
            if 200 <= response.status_code < 300:
                logger.info("Exported %s successfully", description)
            else:
                logger.warning("Exporting %s failed: %s", description, response.status_code)
        except Exception as exc:
            logger.error("Failed to export %s: %s", description, exc)

    # --------------------------------------------------------------------- #
    # Public lifecycle
    # --------------------------------------------------------------------- #

    def flush(self):
        """
        Flush any pending signals immediately.
        Non-blocking - triggers immediate export of pending batch.
        Thread-safe - can be called concurrently.
        """
        with self._condition:
            self._flush_requested = True
            self._condition.notify()  # Wake up export thread immediately
        logger.debug("Flush requested - pending signals will be exported immediately")

    def close(self):
        """Stop exporter and cleanup."""
        # Flush any pending signals before closing
        self.flush()
        self.running = False
        self.export_thread.join(timeout=5.0)
        self.request_thread.join(timeout=5.0)
        logger.info("Signal exporter stopped")

    # --------------------------------------------------------------------- #
    # Utility helpers
    # --------------------------------------------------------------------- #

    def _detect_container_id(self) -> Optional[str]:
        """Attempt to detect the container identifier (if running in Docker)."""
        hostname = os.environ.get("HOSTNAME")
        if hostname and len(hostname) >= 6:
            logger.debug("Detected container ID from HOSTNAME: %s", hostname)
            return hostname

        try:
            with open("/proc/self/cgroup", "r", encoding="utf-8") as cgroup_file:
                for line in cgroup_file:
                    parts = line.strip().split("/")
                    if parts and parts[-1]:
                        candidate = parts[-1]
                        if len(candidate) >= 6:
                            logger.debug("Detected container ID from cgroup: %s", candidate)
                            return candidate
        except OSError:
            logger.debug(
                "Unable to read /proc/self/cgroup for container ID detection",
                exc_info=True,
            )

        logger.debug("Container ID could not be detected")
        return None

    def _ensure_container_id(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Guarantee that each payload has the detected container identifier."""
        if self.container_id:
            payload["container_id"] = self.container_id
        return payload

    def _enqueue_request_event(self, event: Dict[str, Any]):
        try:
            self.request_queue.put_nowait(event)
        except queue.Full:
            logger.warning("Request queue full, dropping event")

    def _derive_related_endpoint(self, signals_endpoint: str, suffix: str) -> str:
        """
        Derive the related request endpoint from the signals endpoint.

        Example:
            signals endpoint: http://host/api/signals/batch
            derived payload:  http://host/api/requests/payload
        """
        base = signals_endpoint
        if "/signals" in signals_endpoint:
            base = signals_endpoint.split("/signals", 1)[0]
        return f"{base}/requests/{suffix}"

    def _build_request_body(
        self,
        field_name: str,
        request_id: str,
        payload: Dict[str, Any],
        metadata: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "request_id": request_id,
            "timestamp": time.time(),
            "metadata": metadata or {},
        }
        if self.container_id:
            body["container_id"] = self.container_id
        body[field_name] = payload
        return body
