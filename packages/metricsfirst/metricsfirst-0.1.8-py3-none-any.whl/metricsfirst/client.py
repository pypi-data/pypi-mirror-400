"""
Synchronous MetricsFirst client
"""

import atexit
import json
import logging
import threading
import time
import weakref
from dataclasses import asdict
from queue import Queue, Empty
from typing import Optional, List, Dict, Any
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from .types import (
    ServiceEventData,
    ErrorEventData,
    PurchaseEventData,
    PurchaseStatus,
    RecurringChargeEventData,
    UserIdentifyData,
)

logger = logging.getLogger("metricsfirst")

# Global registry for cleanup
_instances: weakref.WeakSet["MetricsFirst"] = weakref.WeakSet()
_atexit_registered = False


def _atexit_flush() -> None:
    """Flush all instances on program exit."""
    for instance in list(_instances):
        try:
            instance.shutdown()
        except Exception:
            pass


def _register_atexit() -> None:
    """Register atexit handler once."""
    global _atexit_registered
    if not _atexit_registered:
        atexit.register(_atexit_flush)
        _atexit_registered = True


class MetricsFirst:
    """
    Synchronous MetricsFirst SDK client.
    
    Note: Commands and interactions are tracked automatically.
    Use this SDK to track custom events like services, purchases, and errors.
    
    Usage:
        # Initialize once (globally)
        mf = MetricsFirst(bot_id="your_bot_id", api_key="your_api_key")
        
        # Just use it
        mf.track_service(ServiceEventData(user_id=123, service_name="generation"))
        
        # Events are automatically flushed when program exits
        # No need to call shutdown()!
    """
    
    DEFAULT_API_URL = "https://metricsfirst.io/api"
    
    def __init__(
        self,
        bot_id: str,
        api_key: str,
        api_url: Optional[str] = None,
        batch_events: bool = True,
        batch_size: int = 10,
        batch_interval: float = 5.0,
        debug: bool = False,
        timeout: float = 10.0,
    ):
        """
        Initialize the MetricsFirst client.
        
        Args:
            bot_id: Your bot's unique identifier
            api_key: Your API key from MetricsFirst dashboard
            api_url: Custom API URL (optional)
            batch_events: Whether to batch events before sending
            batch_size: Number of events per batch
            batch_interval: Seconds between batch flushes
            debug: Enable debug logging
            timeout: HTTP request timeout in seconds
        """
        self.bot_id = bot_id
        self.api_key = api_key
        self.api_url = (api_url or self.DEFAULT_API_URL).rstrip("/")
        self.batch_events = batch_events
        self.batch_size = batch_size
        self.batch_interval = batch_interval
        self.timeout = timeout
        
        if debug:
            logging.basicConfig(level=logging.DEBUG)
            logger.setLevel(logging.DEBUG)
        
        # Max 1000 events in queue to prevent memory issues
        self._queue: Queue = Queue(maxsize=1000)
        self._shutdown_event = threading.Event()
        self._worker_thread: Optional[threading.Thread] = None
        
        # Register for automatic cleanup
        _register_atexit()
        _instances.add(self)
        
        if batch_events:
            self._start_worker()
    
    def _start_worker(self):
        """Start the background worker thread for batching"""
        self._worker_thread = threading.Thread(target=self._worker, daemon=True)
        self._worker_thread.start()
    
    def _worker(self):
        """Background worker that flushes events periodically"""
        events: List[Dict[str, Any]] = []
        last_flush = time.time()
        
        while not self._shutdown_event.is_set():
            try:
                # Try to get an event with timeout
                event = self._queue.get(timeout=0.1)
                events.append(event)
                
                # Flush if batch is full
                if len(events) >= self.batch_size:
                    self._flush_events(events)
                    events = []
                    last_flush = time.time()
            except Empty:
                pass
            
            # Flush if interval has passed
            if events and (time.time() - last_flush) >= self.batch_interval:
                self._flush_events(events)
                events = []
                last_flush = time.time()
        
        # Flush remaining events on shutdown
        while not self._queue.empty():
            try:
                events.append(self._queue.get_nowait())
            except Empty:
                break
        
        if events:
            self._flush_events(events)
    
    def _flush_events(self, events: List[Dict[str, Any]]):
        """Send a batch of events to the API"""
        if not events:
            return
        
        try:
            for event in events:
                self._send_event(event["type"], event["data"])
        except Exception as e:
            logger.error(f"Failed to flush events: {e}")
    
    def _send_event(self, event_type: str, data: Dict[str, Any]):
        """Send a single event to the API"""
        payload = {
            "botId": self.bot_id,
            "type": event_type,
            "data": data,
        }
        
        # URL: base/analytics/track (base already includes /api if provided)
        url = f"{self.api_url}/analytics/track"
        
        try:
            request = Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key,
                },
                method="POST",
            )
            
            with urlopen(request, timeout=self.timeout) as response:
                if response.status != 200:
                    response_body = response.read().decode("utf-8")
                    logger.warning(f"API returned status {response.status} for {url}: {response_body}")
                else:
                    logger.debug(f"Event sent: {event_type}")
                    
        except HTTPError as e:
            # Read error response body to get detailed error message
            try:
                error_body = e.read().decode("utf-8")
                error_data = json.loads(error_body)
                error_message = error_data.get("error", e.reason)
            except Exception:
                error_message = e.reason
            logger.warning(f"API returned status {e.code} for {url}: {error_message}")
        except URLError as e:
            logger.error(f"URL error sending event: {e.reason}")
        except Exception as e:
            logger.error(f"Error sending event: {e}")
    
    def _track(self, event_type: str, data: Dict[str, Any]):
        """Queue or send an event (non-blocking, fire-and-forget)"""
        if self.batch_events:
            # Non-blocking put to queue - background thread will handle sending
            try:
                self._queue.put_nowait({"type": event_type, "data": data})
            except Exception:
                logger.warning("Event queue full, dropping event")
        else:
            # Send in background thread to avoid blocking
            threading.Thread(
                target=self._send_event,
                args=(event_type, data),
                daemon=True
            ).start()
    
    def _clean_dict(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """Remove None values and convert enums"""
        result = {}
        for k, v in d.items():
            if v is None:
                continue
            if hasattr(v, "value"):  # Enum
                result[k] = v.value
            elif isinstance(v, dict):
                result[k] = self._clean_dict(v)
            else:
                result[k] = v
        return result
    
    # ==========================================
    # Tracking Methods (fire-and-forget, non-blocking)
    # Note: Commands/interactions are tracked automatically
    # ==========================================
    
    def track(
        self,
        user_id: int,
        event_name: str,
        properties: Optional[Dict[str, Any]] = None,
    ):
        """
        Track a custom event with dynamic properties.
        
        Args:
            user_id: User ID (Telegram user ID)
            event_name: Name of the event (e.g., 'STORY_RESPONSE', 'BUTTON_CLICK')
            properties: Dictionary of event properties (any key-value pairs)
        
        Example:
            mf.track(123456, 'STORY_RESPONSE', {
                'target': 'username123',
                'url': 'https://example.com/story',
                'response_time_ms': 150,
                'success': True
            })
        """
        data = {
            "eventName": event_name,
            "properties": properties or {},
            "userId": user_id,
            "lib": "python",
            "libVersion": "1.0.0",
        }
        
        self._track("custom", data)
    
    def track_service(self, data: ServiceEventData):
        """Track a service provided"""
        self._track("service_provided", self._clean_dict(asdict(data)))
    
    def track_error(self, data: ErrorEventData):
        """Track an error"""
        self._track("error", self._clean_dict(asdict(data)))
    
    def track_error_from_exception(
        self,
        exception: Exception,
        user_id: Optional[int] = None,
        severity: str = "error",
        context: Optional[Dict[str, Any]] = None,
    ):
        """Track an error from an exception"""
        import traceback
        
        data = ErrorEventData(
            error_type=type(exception).__name__,
            error_message=str(exception),
            user_id=user_id,
            error_stack=traceback.format_exc(),
            severity=severity,
            context=context or {},
        )
        self.track_error(data)
    
    def track_purchase_initiated(self, data: PurchaseEventData):
        """Track a purchase initiation"""
        data.status = PurchaseStatus.INITIATED
        self._track("purchase_initiated", self._clean_dict(asdict(data)))
    
    def track_purchase_completed(self, data: PurchaseEventData):
        """Track a completed purchase"""
        data.status = PurchaseStatus.COMPLETED
        self._track("purchase_completed", self._clean_dict(asdict(data)))
    
    def track_purchase_error(self, data: PurchaseEventData):
        """Track a failed purchase"""
        data.status = PurchaseStatus.FAILED
        self._track("purchase_error", self._clean_dict(asdict(data)))
    
    def track_recurring_charge_success(self, data: RecurringChargeEventData):
        """Track a successful recurring charge"""
        data.is_success = True
        self._track("recurring_charge_success", self._clean_dict(asdict(data)))
    
    def track_recurring_charge_failed(self, data: RecurringChargeEventData):
        """Track a failed recurring charge"""
        data.is_success = False
        self._track("recurring_charge_failed", self._clean_dict(asdict(data)))
    
    def identify(self, data: UserIdentifyData):
        """Identify a user with properties"""
        payload = self._clean_dict(asdict(data))
        
        try:
            request = Request(
                f"{self.api_url}/api/users/identify",
                data=json.dumps({
                    "botId": self.bot_id,
                    **payload,
                }).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key,
                },
                method="POST",
            )
            
            with urlopen(request, timeout=self.timeout) as response:
                if response.status != 200:
                    logger.warning(f"Identify returned status {response.status}")
                    
        except Exception as e:
            logger.error(f"Error identifying user: {e}")
    
    def flush(self):
        """Manually flush all pending events"""
        if not self.batch_events:
            return
        
        events = []
        while not self._queue.empty():
            try:
                events.append(self._queue.get_nowait())
            except Empty:
                break
        
        self._flush_events(events)
    
    def shutdown(self):
        """Shutdown the client and flush remaining events"""
        self._shutdown_event.set()
        
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=5.0)
        
        logger.debug("MetricsFirst client shutdown complete")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

