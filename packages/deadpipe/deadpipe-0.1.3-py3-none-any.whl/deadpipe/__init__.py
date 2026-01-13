"""
Deadpipe - Dead simple pipeline monitoring.

Usage:
    from deadpipe import Deadpipe
    
    dp = Deadpipe("your-api-key")
    
    # Option 1: Decorator
    @dp.heartbeat("my-pipeline")
    def my_job():
        # your code here
        pass
    
    # Option 2: Context manager
    with dp.pipeline("my-pipeline"):
        # your code here
        pass
    
    # Option 3: Manual
    dp.ping("my-pipeline", status="success")

Async Usage:
    from deadpipe import AsyncDeadpipe
    
    dp = AsyncDeadpipe("your-api-key")
    
    # Option 1: Decorator
    @dp.heartbeat("my-pipeline")
    async def my_job():
        # your async code here
        pass
    
    # Option 2: Context manager
    async with dp.pipeline("my-pipeline"):
        # your async code here
        pass
    
    # Option 3: Manual
    await dp.ping("my-pipeline", status="success")
"""

import os
import time
import functools
from contextlib import contextmanager, asynccontextmanager
from typing import Optional, Literal, Callable, Any, TypeVar
import urllib.request
import urllib.error
import json

__version__ = "0.1.3"

StatusType = Literal["success", "failed"]
T = TypeVar("T")


class Deadpipe:
    """Dead simple pipeline monitoring client."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://www.deadpipe.com/api/v1",
        timeout: int = 10,
    ):
        """
        Initialize Deadpipe client.
        
        Args:
            api_key: Your Deadpipe API key. Falls back to DEADPIPE_API_KEY env var.
            base_url: API base URL (override for self-hosted).
            timeout: Request timeout in seconds.
        """
        self.api_key = api_key or os.environ.get("DEADPIPE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key required. Pass api_key or set DEADPIPE_API_KEY environment variable."
            )
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
    
    def ping(
        self,
        pipeline_id: str,
        status: StatusType = "success",
        duration_ms: Optional[int] = None,
        records_processed: Optional[int] = None,
        app_name: Optional[str] = None,
    ) -> bool:
        """
        Send a heartbeat ping for a pipeline.
        
        Args:
            pipeline_id: Unique identifier for this pipeline.
            status: "success" or "failed".
            duration_ms: How long the pipeline took (optional).
            records_processed: Number of records processed (optional).
            app_name: Group pipelines under an app name (optional).
        
        Returns:
            True if the ping was sent successfully.
        """
        payload = {
            "pipeline_id": pipeline_id,
            "status": status,
        }
        
        if duration_ms is not None:
            payload["duration_ms"] = duration_ms
        if records_processed is not None:
            payload["records_processed"] = records_processed
        if app_name is not None:
            payload["app_name"] = app_name
        
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                f"{self.base_url}/heartbeat",
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key,
                },
                method="POST",
            )
            
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                return response.status == 200
                
        except urllib.error.URLError:
            # Fail silently - don't break the user's pipeline
            return False
        except Exception:
            return False
    
    def heartbeat(
        self,
        pipeline_id: str,
        app_name: Optional[str] = None,
        on_error: Literal["ping", "raise", "ignore"] = "ping",
    ) -> Callable:
        """
        Decorator to automatically send heartbeats for a function.
        
        Args:
            pipeline_id: Unique identifier for this pipeline.
            app_name: Group pipelines under an app name (optional).
            on_error: What to do if the function raises:
                - "ping": Send failed heartbeat, then re-raise (default)
                - "raise": Re-raise without sending heartbeat
                - "ignore": Send success heartbeat anyway
        
        Example:
            @dp.heartbeat("daily-etl")
            def my_pipeline():
                # do stuff
                return {"records_processed": 1000}
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    duration_ms = int((time.time() - start_time) * 1000)
                    
                    # Extract records_processed from return value if present
                    records = None
                    if isinstance(result, dict):
                        records = result.get("records_processed")
                    
                    self.ping(
                        pipeline_id,
                        status="success",
                        duration_ms=duration_ms,
                        records_processed=records,
                        app_name=app_name,
                    )
                    return result
                    
                except Exception as e:
                    duration_ms = int((time.time() - start_time) * 1000)
                    
                    if on_error == "ping":
                        self.ping(
                            pipeline_id,
                            status="failed",
                            duration_ms=duration_ms,
                            app_name=app_name,
                        )
                        raise
                    elif on_error == "raise":
                        raise
                    else:  # ignore
                        self.ping(
                            pipeline_id,
                            status="success",
                            duration_ms=duration_ms,
                            app_name=app_name,
                        )
                        raise
            
            return wrapper
        return decorator
    
    @contextmanager
    def pipeline(
        self,
        pipeline_id: str,
        app_name: Optional[str] = None,
    ):
        """
        Context manager to automatically send heartbeats.
        
        Example:
            with dp.pipeline("daily-etl"):
                # do stuff
                pass
        """
        start_time = time.time()
        status: StatusType = "success"
        
        try:
            yield
        except Exception:
            status = "failed"
            raise
        finally:
            duration_ms = int((time.time() - start_time) * 1000)
            self.ping(pipeline_id, status=status, duration_ms=duration_ms, app_name=app_name)


class AsyncDeadpipe:
    """Async pipeline monitoring client for use with asyncio/FastAPI/aiohttp."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://www.deadpipe.com/api/v1",
        timeout: int = 10,
    ):
        """
        Initialize async Deadpipe client.
        
        Args:
            api_key: Your Deadpipe API key. Falls back to DEADPIPE_API_KEY env var.
            base_url: API base URL (override for self-hosted).
            timeout: Request timeout in seconds.
        
        Requires: pip install deadpipe[async]
        """
        self.api_key = api_key or os.environ.get("DEADPIPE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key required. Pass api_key or set DEADPIPE_API_KEY environment variable."
            )
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session: Optional[Any] = None
    
    def _get_aiohttp(self):
        """Lazy import aiohttp to avoid requiring it for sync-only users."""
        try:
            import aiohttp
            return aiohttp
        except ImportError:
            raise ImportError(
                "aiohttp is required for async support. "
                "Install with: pip install deadpipe[async]"
            )
    
    async def _get_session(self):
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            aiohttp = self._get_aiohttp()
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session
    
    async def close(self):
        """Close the underlying HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def ping(
        self,
        pipeline_id: str,
        status: StatusType = "success",
        duration_ms: Optional[int] = None,
        records_processed: Optional[int] = None,
        app_name: Optional[str] = None,
    ) -> bool:
        """
        Send a heartbeat ping for a pipeline (async).
        
        Args:
            pipeline_id: Unique identifier for this pipeline.
            status: "success" or "failed".
            duration_ms: How long the pipeline took (optional).
            records_processed: Number of records processed (optional).
            app_name: Group pipelines under an app name (optional).
        
        Returns:
            True if the ping was sent successfully.
        """
        payload = {
            "pipeline_id": pipeline_id,
            "status": status,
        }
        
        if duration_ms is not None:
            payload["duration_ms"] = duration_ms
        if records_processed is not None:
            payload["records_processed"] = records_processed
        if app_name is not None:
            payload["app_name"] = app_name
        
        try:
            session = await self._get_session()
            async with session.post(
                f"{self.base_url}/heartbeat",
                json=payload,
                headers={"X-API-Key": self.api_key},
            ) as response:
                return response.status == 200
        except Exception:
            # Fail silently - don't break the user's pipeline
            return False
    
    def heartbeat(
        self,
        pipeline_id: str,
        app_name: Optional[str] = None,
        on_error: Literal["ping", "raise", "ignore"] = "ping",
    ) -> Callable:
        """
        Decorator to automatically send heartbeats for an async function.
        
        Args:
            pipeline_id: Unique identifier for this pipeline.
            app_name: Group pipelines under an app name (optional).
            on_error: What to do if the function raises:
                - "ping": Send failed heartbeat, then re-raise (default)
                - "raise": Re-raise without sending heartbeat
                - "ignore": Send success heartbeat anyway
        
        Example:
            @dp.heartbeat("daily-etl")
            async def my_pipeline():
                # do async stuff
                return {"records_processed": 1000}
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                start_time = time.time()
                
                try:
                    result = await func(*args, **kwargs)
                    duration_ms = int((time.time() - start_time) * 1000)
                    
                    # Extract records_processed from return value if present
                    records = None
                    if isinstance(result, dict):
                        records = result.get("records_processed")
                    
                    await self.ping(
                        pipeline_id,
                        status="success",
                        duration_ms=duration_ms,
                        records_processed=records,
                        app_name=app_name,
                    )
                    return result
                    
                except Exception:
                    duration_ms = int((time.time() - start_time) * 1000)
                    
                    if on_error == "ping":
                        await self.ping(
                            pipeline_id,
                            status="failed",
                            duration_ms=duration_ms,
                            app_name=app_name,
                        )
                        raise
                    elif on_error == "raise":
                        raise
                    else:  # ignore
                        await self.ping(
                            pipeline_id,
                            status="success",
                            duration_ms=duration_ms,
                            app_name=app_name,
                        )
                        raise
            
            return wrapper
        return decorator
    
    @asynccontextmanager
    async def pipeline(
        self,
        pipeline_id: str,
        app_name: Optional[str] = None,
    ):
        """
        Async context manager to automatically send heartbeats.
        
        Example:
            async with dp.pipeline("daily-etl"):
                # do async stuff
                pass
        """
        start_time = time.time()
        status: StatusType = "success"
        
        try:
            yield
        except Exception:
            status = "failed"
            raise
        finally:
            duration_ms = int((time.time() - start_time) * 1000)
            await self.ping(pipeline_id, status=status, duration_ms=duration_ms, app_name=app_name)
    
    async def run(
        self,
        pipeline_id: str,
        fn: Callable[..., Any],
        *args: Any,
        app_name: Optional[str] = None,
        **kwargs: Any,
    ) -> Any:
        """
        Run an async function with automatic heartbeat on completion.
        
        Args:
            pipeline_id: Unique identifier for this pipeline.
            fn: The async function to run.
            *args: Positional arguments to pass to fn.
            app_name: Group pipelines under an app name (optional).
            **kwargs: Keyword arguments to pass to fn.
        
        Returns:
            The result of the function.
        
        Example:
            result = await dp.run("daily-etl", process_data, records)
        """
        start_time = time.time()
        status: StatusType = "success"
        records_processed = None
        
        try:
            result = await fn(*args, **kwargs)
            
            if isinstance(result, dict):
                records_processed = result.get("records_processed")
            
            return result
        except Exception:
            status = "failed"
            raise
        finally:
            duration_ms = int((time.time() - start_time) * 1000)
            await self.ping(
                pipeline_id,
                status=status,
                duration_ms=duration_ms,
                records_processed=records_processed,
                app_name=app_name,
            )


# Convenience: module-level functions using env var
_default_client: Optional[Deadpipe] = None


def _get_client() -> Deadpipe:
    global _default_client
    if _default_client is None:
        _default_client = Deadpipe()
    return _default_client


def ping(
    pipeline_id: str,
    status: StatusType = "success",
    duration_ms: Optional[int] = None,
    records_processed: Optional[int] = None,
    app_name: Optional[str] = None,
) -> bool:
    """Send a heartbeat using DEADPIPE_API_KEY from environment."""
    return _get_client().ping(pipeline_id, status, duration_ms, records_processed, app_name)


def heartbeat(pipeline_id: str, app_name: Optional[str] = None) -> Callable:
    """Decorator using DEADPIPE_API_KEY from environment."""
    return _get_client().heartbeat(pipeline_id, app_name)


# Export both sync and async classes
__all__ = ["Deadpipe", "AsyncDeadpipe", "ping", "heartbeat"]

