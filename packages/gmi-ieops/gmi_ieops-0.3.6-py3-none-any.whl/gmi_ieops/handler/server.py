# /root/code/python/ieops-python/sdk/src/handler/server.py
"""
Server - FastAPI Server

Provides common server infrastructure with dynamic route registration.
Users can freely combine predefined routes or custom routes.

Usage:
```python
from gmi_ieops.handler import Handler, Server, RouterDef, RouterConfig

# Pass route config directly, APIRouter is created internally
routes = {
    "v1": [
        RouterDef(path="chat", handler=model.chat, kind="sse"),
        RouterDef(path="status", handler=get_status, kind="api"),
    ],
}
server = Server(routers=routes)
Handler(server=server).serve()

# With configuration
config = RouterConfig(timeout=600)
server = Server(routers=routes, router_config=config, prefix="/api")
```
"""

import os
import traceback
from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine, Dict, List, Optional
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from ..utils.log import uvicorn_logger
from ..utils.util import get_socket_path
from ..config import env
from .router import RouterDef, RouterConfig, RouterGroupConfig, create_router_from_config, RouterError

# Type alias
LifecycleHook = Callable[[], Coroutine[Any, Any, None]]


class ServerError(Exception):
    """Server error - Users can yield this type in inference_func to indicate an error"""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class BaseServer(ABC):
    """Server base class"""
    
    @abstractmethod
    def shutdown(self) -> None:
        """request server graceful shutdown"""
    
    @abstractmethod
    async def serve(self) -> None:
        """serve the server"""


class Server(BaseServer):
    """
    Unified FastAPI Server - Only handles infrastructure
    
    Features:
    - Dynamic route registration: Pass route config directly, auto-creates APIRouter
    - Lifecycle management: Supports custom on_startup/on_shutdown callbacks
    - Flexible configuration: Supports both socket and host:port listening
    - CORS support: Optionally enable cross-origin
    
    Attributes:
        routers: Route config dict {group_name: [RouterDef, ...]}
        router_config: Route config (timeout, SSE headers, etc.)
        prefix: Route prefix
        on_startup: Startup callback (async function)
        on_shutdown: Shutdown callback (async function)
        enable_cors: Whether to enable CORS
        cors_origins: CORS allowed origins
        app_name: Application name (for logging)
    """
    
    def __init__(
        self,
        routers: Optional[RouterGroupConfig] = None,
        router_config: Optional[RouterConfig] = None,
        prefix: str = "",
        on_startup: Optional[LifecycleHook] = None,
        on_shutdown: Optional[LifecycleHook] = None,
        enable_cors: bool = False,
        cors_origins: Optional[List[str]] = None,
        app_name: str = "ieops",
        # Allow overriding default config
        socket_path: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ) -> None:
        """
        Initialize unified server
        
        Args:
            routers: Route configuration dict {group_name: [RouterDef, ...]}
            router_config: Route configuration (timeout, SSE headers, etc.)
            prefix: Route prefix
            on_startup: Callback function when server starts
            on_shutdown: Callback function when server shuts down
            enable_cors: Whether to enable CORS middleware
            cors_origins: CORS allowed origins list, defaults to ["*"]
            app_name: Application name
            socket_path: Unix socket path (overrides environment variable)
            host: Listen address (overrides environment variable)
            port: Listen port (overrides environment variable)
        """
        self._on_startup = on_startup
        self._on_shutdown = on_shutdown
        self._app_name = app_name
        
        # Priority: parameters > config
        # Server mode selection:
        # - If socket_path parameter is explicitly provided, use it
        # - Else if port is set (> 0), use TCP mode (socket_path = None)
        # - Else use Unix socket mode
        self._host = host if host is not None else env.server.host
        self._port = port if port is not None else env.server.port
        
        if socket_path is not None:
            # Explicit socket_path parameter provided
            self._socket_path = socket_path if socket_path else None
        elif self._port > 0:
            # Port is set, use TCP mode
            self._socket_path = None
        else:
            # Port not set, use Unix socket mode
            # Path format: {socket_dir}/{APP_ID}.sock
            self._socket_path = get_socket_path()
        
        # Create FastAPI application
        self._app = FastAPI(
            title=app_name,
            lifespan=self._lifespan,
        )
        self._server: Optional[uvicorn.Server] = None
        
        # Enable CORS
        if enable_cors:
            self._app.add_middleware(
                CORSMiddleware,
                allow_origins=cors_origins or ["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        
        # Register global exception handlers
        self._setup_exception_handlers()
        
        # Register base routes
        self._setup_base_routes()
        
        # Create and register routes based on config
        if routers:
            router = create_router_from_config(routers, router_config, prefix)
            self._app.include_router(router)
    
    @property
    def app(self) -> FastAPI:
        """Get FastAPI application instance (for advanced customization)"""
        return self._app
    
    def add_middleware(self, middleware_class, **options) -> None:
        """
        Add middleware
        
        Args:
            middleware_class: Middleware class
            **options: Middleware options
        """
        self._app.add_middleware(middleware_class, **options)
    
    def _setup_exception_handlers(self) -> None:
        """Setup global exception handlers"""
        
        @self._app.exception_handler(StarletteHTTPException)
        async def http_exception_handler(request: Request, exc: StarletteHTTPException):
            """HTTP exception handler"""
            uvicorn_logger.warning(f"HTTP {exc.status_code}: {exc.detail} - {request.url.path}")
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "message": exc.detail,
                    "type": "http_error",
                }
            )
        
        @self._app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError):
            """Request validation error handler"""
            errors = []
            for error in exc.errors():
                errors.append({
                    "field": ".".join(str(loc) for loc in error.get("loc", [])),
                    "message": error.get("msg", ""),
                    "type": error.get("type", ""),
                })
            uvicorn_logger.warning(f"Validation error: {errors} - {request.url.path}")
            return JSONResponse(
                status_code=422,
                content={
                    "message": "Request validation failed",
                    "type": "validation_error",
                    "details": errors,
                }
            )
        
        @self._app.exception_handler(RouterError)
        async def router_error_handler(request: Request, exc: RouterError):
            """Router error handler"""
            uvicorn_logger.error(f"Router error: {exc} - {request.url.path}")
            return JSONResponse(
                status_code=500,
                content={
                    "message": str(exc),
                    "type": "router_error",
                }
            )
        
        @self._app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            """General exception handler"""
            uvicorn_logger.error(f"Unhandled exception: {exc} - {request.url.path}\n{traceback.format_exc()}")
            return JSONResponse(
                status_code=500,
                content={
                    "message": "Internal server error",
                    "type": "internal_error",
                }
            )
    
    @asynccontextmanager
    async def _lifespan(self, app: FastAPI):
        """FastAPI lifecycle management"""
        uvicorn_logger.info(f"{self._app_name} UnifiedServer starting...")
        
        # Execute startup callback
        if self._on_startup:
            try:
                await self._on_startup()
            except Exception as e:
                uvicorn_logger.error(f"on_startup error: {e}")
                raise
        
        yield
        
        # Execute shutdown callback
        uvicorn_logger.info(f"{self._app_name} UnifiedServer shutting down...")
        if self._on_shutdown:
            try:
                await self._on_shutdown()
            except Exception as e:
                uvicorn_logger.error(f"on_shutdown error: {e}")
        
        # Clean up socket file
        if self._socket_path and os.path.exists(self._socket_path):
            try:
                os.remove(self._socket_path)
                uvicorn_logger.info(f"Removed socket file: {self._socket_path}")
            except Exception as e:
                uvicorn_logger.error(f"Failed to remove socket file: {e}")
    
    def _setup_base_routes(self) -> None:
        """Setup base routes"""
        @self._app.get("/")
        async def root():
            """Root path - Service info"""
            routes = []
            for route in self._app.routes:
                if hasattr(route, "path") and hasattr(route, "methods"):
                    routes.append({
                        "path": route.path,
                        "methods": list(route.methods) if route.methods else [],
                    })
            
            return {
                "service": self._app_name,
                "status": "running",
                "routes_count": len(routes),
            }
        
        @self._app.get("/health")
        async def health():
            """Health check"""
            return {"status": "ok"}
        
        @self._app.get("/routes")
        async def list_routes():
            """List all routes (for debugging)"""
            routes = []
            for route in self._app.routes:
                if hasattr(route, "path") and hasattr(route, "methods"):
                    routes.append({
                        "path": route.path,
                        "methods": list(route.methods) if route.methods else [],
                        "name": route.name if hasattr(route, "name") else None,
                    })
            return {"routes": routes}
    
    def shutdown(self) -> None:
        """Request server graceful shutdown"""
        if self._server:
            self._server.should_exit = True
    
    async def serve(self) -> None:
        """Start server"""
        # Build uvicorn config
        if self._socket_path:
            uvicorn_logger.info(f"Starting server on unix socket: {self._socket_path}")
            uvicorn_config = uvicorn.Config(
                self._app,
                uds=self._socket_path,
                log_level="info",
                loop="asyncio",
                timeout_graceful_shutdown=env.server.graceful_shutdown_time,
            )
        else:
            uvicorn_logger.info(f"Starting server on {self._host}:{self._port}")
            uvicorn_config = uvicorn.Config(
                self._app,
                host=self._host,
                port=self._port,
                log_level="info",
                loop="asyncio",
                timeout_graceful_shutdown=env.server.graceful_shutdown_time,
            )
        
        self._server = uvicorn.Server(uvicorn_config)
        await self._server.serve()


# Alias for backward compatibility
UnifiedServer = Server
