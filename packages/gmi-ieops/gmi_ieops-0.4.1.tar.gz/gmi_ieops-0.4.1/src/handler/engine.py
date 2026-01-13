"""
Engine Module - Unified management for Register and Interceptor

Provides a simple interface to start Register and/or Interceptor
for user services.

Usage:
```python
from gmi_ieops.handler import Engine
from gmi_ieops.utils import get_service_port

port = get_service_port()

# Start engine (auto cleanup on exit)
engine = Engine(
    service_port=port,
    register_enable=True,
    interceptor_enable=True,
)
engine.start()

# Start your service
app.run(host="127.0.0.1", port=port)
```
"""

import os
import atexit
import signal
import asyncio
import multiprocessing
from typing import Optional, Callable, Any

from ..utils.log import uvicorn_logger
from ..utils.util import get_socket_path
from ..config import env


# Global engine process for cleanup
_engine_process: Optional[multiprocessing.Process] = None
_original_sigint_handler: Optional[Callable] = None
_original_sigterm_handler: Optional[Callable] = None


def _cleanup_engine():
    """Cleanup engine subprocess on exit"""
    global _engine_process
    if _engine_process is not None and _engine_process.is_alive():
        uvicorn_logger.info("Stopping engine subprocess...")
        _engine_process.terminate()
        _engine_process.join(timeout=5)
        if _engine_process.is_alive():
            _engine_process.kill()
            _engine_process.join(timeout=1)
        _engine_process = None


def _signal_handler(signum, frame):
    """Handle signals - cleanup engine then call original handler"""
    global _original_sigint_handler, _original_sigterm_handler
    
    # Cleanup engine subprocess
    _cleanup_engine()
    
    # Call original handler if exists
    if signum == signal.SIGINT and _original_sigint_handler:
        if callable(_original_sigint_handler):
            _original_sigint_handler(signum, frame)
        elif _original_sigint_handler == signal.SIG_DFL:
            signal.signal(signum, signal.SIG_DFL)
            os.kill(os.getpid(), signum)
    elif signum == signal.SIGTERM and _original_sigterm_handler:
        if callable(_original_sigterm_handler):
            _original_sigterm_handler(signum, frame)
        elif _original_sigterm_handler == signal.SIG_DFL:
            signal.signal(signum, signal.SIG_DFL)
            os.kill(os.getpid(), signum)
    else:
        # No original handler, use default behavior
        signal.signal(signum, signal.SIG_DFL)
        os.kill(os.getpid(), signum)


# Register cleanup handlers
atexit.register(_cleanup_engine)


class Engine:
    """
    Unified engine for Register and Interceptor management.
    
    Features:
    - Optionally enable Register (service registration with IEOPS proxy)
    - Optionally enable Interceptor (transparent request proxy)
    - Automatic cleanup on exit
    - Runs in subprocess, user service runs in main process
    
    Example:
        from gmi_ieops.handler import Engine
        from gmi_ieops.utils import get_service_port
        
        port = get_service_port()
        engine = Engine(service_port=port)
        engine.start()
        app.run(host="127.0.0.1", port=port)
    """
    
    def __init__(
        self,
        service_port: Optional[int] = None,
        service_host: str = "127.0.0.1",
        register_enable: bool = True,
        interceptor_enable: bool = True,
        timeout: int = 600,
        app_name: Optional[str] = None,
        socket_path: Optional[str] = None,
    ) -> None:
        """
        Initialize engine.
        
        Args:
            service_port: Port where user service is listening.
                          Required if interceptor_enable=True.
            service_host: Host where user service is listening (default: 127.0.0.1)
            register_enable: Enable service registration with IEOPS proxy
            interceptor_enable: Enable transparent request proxy
            timeout: Request timeout in seconds (for interceptor)
            app_name: Application name (defaults to env.app.name)
            socket_path: Unix socket path (defaults to auto-generated)
        """
        self._service_port = service_port
        self._service_host = service_host
        self._register_enable = register_enable
        self._interceptor_enable = interceptor_enable
        self._timeout = timeout
        self._app_name = app_name or env.app.name
        self._socket_path = socket_path or get_socket_path()
        
        if interceptor_enable and not service_port:
            raise ValueError("service_port is required when interceptor_enable=True")
    
    def start(self) -> None:
        """
        Start engine in subprocess.
        
        The subprocess runs Register and/or Interceptor based on configuration.
        Automatically cleaned up on program exit or signals.
        """
        global _engine_process, _original_sigint_handler, _original_sigterm_handler
        
        _cleanup_engine()
        
        if not self._register_enable and not self._interceptor_enable:
            uvicorn_logger.info("Engine: both register and interceptor disabled, nothing to start")
            return
        
        proc = multiprocessing.Process(
            target=_run_engine,
            args=(
                self._service_port,
                self._service_host,
                self._register_enable,
                self._interceptor_enable,
                self._timeout,
                self._app_name,
                self._socket_path,
            ),
            daemon=False,  # Non-daemon so it can cleanup properly
        )
        proc.start()
        
        _engine_process = proc
        
        # Save original handlers and install ours
        try:
            _original_sigint_handler = signal.signal(signal.SIGINT, _signal_handler)
            _original_sigterm_handler = signal.signal(signal.SIGTERM, _signal_handler)
        except ValueError:
            # Not in main thread
            pass
        
        modes = []
        if self._register_enable:
            modes.append("register")
        if self._interceptor_enable:
            modes.append("interceptor")
        
        uvicorn_logger.info(f"Engine started (PID: {proc.pid}), modes: {', '.join(modes)}")
        if self._interceptor_enable:
            uvicorn_logger.info(f"Forwarding to: http://{self._service_host}:{self._service_port}")


def _run_engine(
    service_port: Optional[int],
    service_host: str,
    register_enable: bool,
    interceptor_enable: bool,
    timeout: int,
    app_name: str,
    socket_path: str,
) -> None:
    """Run engine in subprocess"""
    # Setup signal handlers for graceful shutdown
    shutdown_event = asyncio.Event()
    
    def handle_signal(signum, frame):
        uvicorn_logger.info(f"Engine subprocess received signal {signum}")
        shutdown_event.set()
    
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    
    asyncio.run(_async_run_engine(
        service_port,
        service_host,
        register_enable,
        interceptor_enable,
        timeout,
        app_name,
        socket_path,
        shutdown_event,
    ))


async def _async_run_engine(
    service_port: Optional[int],
    service_host: str,
    register_enable: bool,
    interceptor_enable: bool,
    timeout: int,
    app_name: str,
    socket_path: str,
    shutdown_event: asyncio.Event,
) -> None:
    """Async engine runner - manages Register and Interceptor"""
    from .interceptor import Interceptor
    from .register import Register
    
    uvicorn_logger.info(f"{app_name} Engine starting...")
    
    tasks = []
    interceptor_runner = None
    
    # Start Register if enabled
    if register_enable:
        register = Register()
        register_task = asyncio.create_task(register.register())
        tasks.append(register_task)
        uvicorn_logger.info("Register enabled")
    
    # Start Interceptor if enabled
    if interceptor_enable:
        upstream = f"http://{service_host}:{service_port}"
        interceptor = Interceptor(
            upstream=upstream,
            timeout=timeout,
            app_name=app_name,
            socket_path=socket_path,
        )
        interceptor_runner = await interceptor.serve_async()
        uvicorn_logger.info(f"Interceptor enabled, upstream: {upstream}")
    
    # Wait for shutdown signal
    await shutdown_event.wait()
    
    uvicorn_logger.info(f"{app_name} Engine shutting down...")
    
    # Cleanup Register tasks
    for task in tasks:
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    # Cleanup Interceptor
    if interceptor_runner:
        await interceptor_runner.cleanup()
    
    uvicorn_logger.info(f"{app_name} Engine stopped")
