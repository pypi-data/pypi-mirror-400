"""
OneX Core Monitor
Automatically detects framework and applies appropriate adapter
"""

import logging
from contextlib import contextmanager
from typing import Optional, Dict, Any

from .utils import FrameworkDetector
from .adapters import (
    PyTorchAdapter,
    TensorFlowAdapter,
    JAXAdapter,
)
from .exporters import AsyncSignalExporter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OneXMonitor:
    """
    Universal neural signal monitor
    
    Automatically detects framework (PyTorch/TensorFlow/JAX)
    and applies appropriate monitoring hooks
    
    Args:
        api_key: OneX API key for authentication
        endpoint: OneX API endpoint (default: https://api.onex.io)
        enabled: Enable/disable monitoring (default: True)
        config: Additional configuration options
    
    Example:
        >>> from onex import OneXMonitor
        >>> monitor = OneXMonitor(api_key="your-key")
        >>> model = monitor.watch(model)
        >>> # Model now streams signals to OneX automatically!
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: str = "https://api.onex.io",
        enabled: bool = True,
        config: Optional[Dict[str, Any]] = None
    ):
        self.api_key = api_key
        self.endpoint = endpoint
        self.enabled = enabled
        self.config = config or {}
        
        # Auto-detect framework
        self.detector = FrameworkDetector()
        self.framework = self.detector.detect()
        
        # Initialize signal exporter
        payload_endpoint_override = self.config.get("request_payload_endpoint")
        response_endpoint_override = self.config.get("request_response_endpoint")
        self.exporter = AsyncSignalExporter(
            endpoint=f"{endpoint}/api/signals/batch",
            api_key=api_key,
            request_payload_endpoint=payload_endpoint_override,
            request_response_endpoint=response_endpoint_override,
        )
        
        # Select appropriate adapter
        self.adapter = self._get_adapter()
        
        logger.info(f"OneX Monitor initialized")
        logger.info(f"  Framework detected: {self.framework}")
        logger.info(f"  Endpoint: {endpoint}")
        logger.info(f"  Monitoring: {'Enabled' if enabled else 'Disabled'}")
    
    def _get_adapter(self):
        """Get framework-specific adapter"""
        if self.framework == 'pytorch':
            if PyTorchAdapter is None:
                raise RuntimeError(
                    "PyTorch support is not available. Install the 'pytorch' extra with "
                    "'pip install onex-sdk[pytorch]' to enable it."
                )
            return PyTorchAdapter(self.exporter, self.config)
        elif self.framework == 'tensorflow':
            if TensorFlowAdapter is None:
                raise RuntimeError(
                    "TensorFlow support is not available. Install the 'tensorflow' extra "
                    "with 'pip install onex-sdk[tensorflow]' to enable it."
                )
            return TensorFlowAdapter(self.exporter, self.config)
        elif self.framework == 'jax':
            if JAXAdapter is None:
                raise RuntimeError(
                    "JAX support is not available. Install the 'jax' extra with "
                    "'pip install onex-sdk[jax]' to enable it."
                )
            return JAXAdapter(self.exporter, self.config)
        else:
            raise ValueError(f"Unsupported framework: {self.framework}")
    
    def watch(self, model):
        """
        Start monitoring a model
        
        Args:
            model: The model to monitor (PyTorch/TensorFlow/JAX)
        
        Returns:
            The same model with monitoring hooks attached
        
        Example:
            >>> model = AutoModelForSequenceClassification.from_pretrained("bert-base")
            >>> model = monitor.watch(model)
        """
        if not self.enabled:
            logger.info("OneX monitoring is disabled, returning model unchanged")
            return model
        
        logger.info(f"Attaching OneX monitoring to {model.__class__.__name__}")
        return self.adapter.attach_monitoring(model)
    
    def stop(self):
        """Stop monitoring and cleanup"""
        self.adapter.cleanup()
        self.exporter.close()
        logger.info("OneX monitoring stopped")

    @contextmanager
    def request_context(
        self,
        payload: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Track a request/response pair around a model invocation.

        Example:
            with monitor.request_context({"text": text}) as req:
                outputs = model(**inputs)
                # build application response
                req.record_response(api_response)
        """
        request_id = self.adapter.start_request_context(payload=payload, metadata=metadata)
        handle = _RequestContextHandle(
            adapter=self.adapter,
            request_id=request_id,
            metadata_override=metadata or {},
        )
        try:
            yield handle
        finally:
            self.adapter.end_request_context()
            # Flush any pending signals immediately after request completes
            self.exporter.flush()


class _RequestContextHandle:
    """Helper exposed by OneXMonitor.request_context for manual instrumentation."""

    def __init__(self, adapter, request_id: str, metadata_override: Dict[str, Any]):
        self._adapter = adapter
        self.request_id = request_id
        self._metadata_override = metadata_override or {}

    def record_response(
        self,
        response: Dict[str, Any],
        *,
        success: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Emit the final application response for this request.

        Args:
            response: Arbitrary JSON-serialisable structure (will be nested under ``response``).
            success: Whether the application request succeeded (defaults to True).
            metadata: Optional extra metadata merged into the request response event.
        """
        extra = dict(metadata or {})
        extra.setdefault("variant", "application_response")
        self._adapter.export_manual_response(
            self.request_id,
            response_payload=response,
            success=success,
            metadata_override=self._metadata_override,
            extra_metadata=extra,
        )
