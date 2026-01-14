"""
Asynchronous MetricsFirst client
"""

import asyncio
import atexit
import json
import logging
import weakref
from dataclasses import asdict
from typing import Optional, List, Dict, Any

try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

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
_async_instances: weakref.WeakSet["AsyncMetricsFirst"] = weakref.WeakSet()
_async_atexit_registered = False


def _async_atexit_flush() -> None:
    """Flush all async instances on program exit."""
    for instance in list(_async_instances):
        try:
            instance._sync_flush_on_exit()
        except Exception:
            pass


def _register_async_atexit() -> None:
    """Register atexit handler once."""
    global _async_atexit_registered
    if not _async_atexit_registered:
        atexit.register(_async_atexit_flush)
        _async_atexit_registered = True


class AsyncMetricsFirst:
    """
    Asynchronous MetricsFirst SDK client.
    
    Note: Commands and interactions are tracked automatically.
    Use this SDK to track custom events like services, purchases, and errors.
    
    Usage:
        # Initialize once (globally)
        mf = AsyncMetricsFirst(bot_id="your_bot_id", api_key="your_api_key")
        
        # Just use it - auto-starts on first call
        mf.track_service(ServiceEventData(user_id=123, service_name="generation"))
        
        # Events are automatically flushed when program exits
        # No need to call start() or shutdown()!
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
        Initialize the AsyncMetricsFirst client.
        
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
        if not HAS_AIOHTTP:
            raise ImportError(
                "aiohttp is required for AsyncMetricsFirst. "
                "Install with: pip install metricsfirst[async]"
            )
        
        self.bot_id = bot_id
        self.api_key = api_key
        self.api_url = (api_url or self.DEFAULT_API_URL).rstrip("/")
        self.batch_events = batch_events
        self.batch_size = batch_size
        self.batch_interval = batch_interval
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        
        if debug:
            logging.basicConfig(level=logging.DEBUG)
            logger.setLevel(logging.DEBUG)
        
        # Max 1000 events in queue to prevent memory issues
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=1000)
        self._session: Optional[aiohttp.ClientSession] = None
        self._worker_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        self._started = False
        
        # Register for automatic cleanup
        _register_async_atexit()
        _async_instances.add(self)
    
    async def start(self):
        """Start the client and background worker"""
        if self._started:
            return
            
        self._session = aiohttp.ClientSession(timeout=self.timeout)
        self._shutdown_event.clear()
        self._started = True
        
        if self.batch_events:
            self._worker_task = asyncio.create_task(self._worker())
        
        logger.debug("AsyncMetricsFirst client started")
    
    async def _worker(self):
        """Background worker that flushes events periodically"""
        events: List[Dict[str, Any]] = []
        
        while not self._shutdown_event.is_set():
            try:
                # Try to get an event with timeout
                event = await asyncio.wait_for(
                    self._queue.get(),
                    timeout=self.batch_interval
                )
                events.append(event)
                
                # Flush if batch is full
                if len(events) >= self.batch_size:
                    await self._flush_events(events)
                    events = []
                    
            except asyncio.TimeoutError:
                # Timeout - flush what we have
                if events:
                    await self._flush_events(events)
                    events = []
            except asyncio.CancelledError:
                break
        
        # Flush remaining events on shutdown
        while not self._queue.empty():
            try:
                events.append(self._queue.get_nowait())
            except asyncio.QueueEmpty:
                break
        
        if events:
            await self._flush_events(events)
    
    async def _flush_events(self, events: List[Dict[str, Any]]):
        """Send a batch of events to the API"""
        if not events:
            return
        
        try:
            tasks = [
                self._send_event(event["type"], event["data"])
                for event in events
            ]
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Failed to flush events: {e}")
    
    async def _send_event(self, event_type: str, data: Dict[str, Any]):
        """Send a single event to the API"""
        if not self._session:
            logger.error("Client not started. Call start() first.")
            return
        
        payload = {
            "botId": self.bot_id,
            "type": event_type,
            "data": data,
        }
        
        # URL: base/analytics/track (base already includes /api if provided)
        url = f"{self.api_url}/analytics/track"
        
        try:
            async with self._session.post(
                url,
                json=payload,
                headers={"X-API-Key": self.api_key},
            ) as response:
                if response.status != 200:
                    text = await response.text()
                    try:
                        error_data = json.loads(text)
                        error_message = error_data.get("error", text[:200])
                    except json.JSONDecodeError:
                        error_message = text[:200]
                    logger.warning(f"API returned status {response.status} for {url}: {error_message}")
                else:
                    logger.debug(f"Event sent: {event_type}")
                    
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error sending event: {e}")
        except Exception as e:
            logger.error(f"Error sending event: {e}")
    
    def _track(self, event_type: str, data: Dict[str, Any]):
        """Queue or send an event (non-blocking, fire-and-forget)"""
        # Auto-start on first event
        if not self._started:
            asyncio.create_task(self._auto_start_and_track(event_type, data))
            return
            
        if self.batch_events:
            # Non-blocking put to queue - background task will handle sending
            try:
                self._queue.put_nowait({"type": event_type, "data": data})
            except asyncio.QueueFull:
                logger.warning("Event queue full, dropping event")
        else:
            # Fire and forget - create task without awaiting
            asyncio.create_task(self._send_event(event_type, data))
    
    async def _auto_start_and_track(self, event_type: str, data: Dict[str, Any]):
        """Auto-start and then track event."""
        await self.start()
        if self.batch_events:
            try:
                self._queue.put_nowait({"type": event_type, "data": data})
            except asyncio.QueueFull:
                logger.warning("Event queue full, dropping event")
        else:
            await self._send_event(event_type, data)
    
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
        """Track a service provided (fire-and-forget)"""
        self._track("service_provided", self._clean_dict(asdict(data)))
    
    def track_error(self, data: ErrorEventData):
        """Track an error (fire-and-forget)"""
        self._track("error", self._clean_dict(asdict(data)))
    
    def track_error_from_exception(
        self,
        exception: Exception,
        user_id: Optional[int] = None,
        severity: str = "error",
        context: Optional[Dict[str, Any]] = None,
    ):
        """Track an error from an exception (fire-and-forget)"""
        import traceback
        
        err_data = ErrorEventData(
            error_type=type(exception).__name__,
            error_message=str(exception),
            user_id=user_id,
            error_stack=traceback.format_exc(),
            severity=severity,
            context=context or {},
        )
        self.track_error(err_data)
    
    def track_purchase_initiated(self, data: PurchaseEventData):
        """Track a purchase initiation (fire-and-forget)"""
        data.status = PurchaseStatus.INITIATED
        self._track("purchase_initiated", self._clean_dict(asdict(data)))
    
    def track_purchase_completed(self, data: PurchaseEventData):
        """Track a completed purchase (fire-and-forget)"""
        data.status = PurchaseStatus.COMPLETED
        self._track("purchase_completed", self._clean_dict(asdict(data)))
    
    def track_purchase_error(self, data: PurchaseEventData):
        """Track a failed purchase (fire-and-forget)"""
        data.status = PurchaseStatus.FAILED
        self._track("purchase_error", self._clean_dict(asdict(data)))
    
    def track_recurring_charge_success(self, data: RecurringChargeEventData):
        """Track a successful recurring charge (fire-and-forget)"""
        data.is_success = True
        self._track("recurring_charge_success", self._clean_dict(asdict(data)))
    
    def track_recurring_charge_failed(self, data: RecurringChargeEventData):
        """Track a failed recurring charge (fire-and-forget)"""
        data.is_success = False
        self._track("recurring_charge_failed", self._clean_dict(asdict(data)))
    
    async def identify(self, data: UserIdentifyData):
        """Identify a user with properties"""
        # Auto-start on first call
        if not self._started:
            await self.start()
        
        payload = self._clean_dict(asdict(data))
        
        try:
            async with self._session.post(
                f"{self.api_url}/api/users/identify",
                json={"botId": self.bot_id, **payload},
                headers={"X-API-Key": self.api_key},
            ) as response:
                if response.status != 200:
                    logger.warning(f"Identify returned status {response.status}")
                    
        except Exception as e:
            logger.error(f"Error identifying user: {e}")
    
    async def flush(self):
        """Manually flush all pending events"""
        if not self.batch_events:
            return
        
        events = []
        while not self._queue.empty():
            try:
                events.append(self._queue.get_nowait())
            except asyncio.QueueEmpty:
                break
        
        await self._flush_events(events)
    
    async def shutdown(self):
        """Shutdown the client and flush remaining events"""
        self._shutdown_event.set()
        
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        
        # Flush any remaining events
        await self.flush()
        
        if self._session:
            await self._session.close()
        
        logger.debug("AsyncMetricsFirst client shutdown complete")
    
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.shutdown()
    
    def _sync_flush_on_exit(self) -> None:
        """Synchronously flush events on program exit."""
        if not self._started or self._queue.empty():
            return

        try:
            # Try to get running loop
            loop = asyncio.get_running_loop()
            # If we're in an async context, schedule the flush
            loop.create_task(self.flush())
        except RuntimeError:
            # No running loop - create one for cleanup
            try:
                asyncio.run(self._cleanup())
            except Exception:
                pass

    async def _cleanup(self) -> None:
        """Async cleanup for atexit."""
        await self.flush()
        if self._session:
            await self._session.close()

