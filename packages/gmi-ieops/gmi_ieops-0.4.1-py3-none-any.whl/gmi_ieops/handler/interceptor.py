"""
Interceptor Module - Transparent request proxy for custom user services

Provides a transparent proxy (like nginx) that forwards requests from
IEOPS proxy to user's custom service implementation.

Note: For unified management of Register + Interceptor, use Engine instead.

Usage:
```python
from gmi_ieops.handler import Engine
from gmi_ieops.utils import get_service_port

port = get_service_port()
engine = Engine(service_port=port)
engine.start()
app.run(host="127.0.0.1", port=port)
```
"""

import os
import asyncio
from typing import Optional

import aiohttp
from aiohttp import web

from ..utils.log import uvicorn_logger
from ..utils.util import get_socket_path
from ..config import env


class Interceptor:
    """
    Transparent Request Proxy using aiohttp
    
    Pure proxy - no business logic, no Register management.
    For Register + Interceptor, use Engine instead.
    
    Features:
    - HTTP request forwarding (all methods)
    - WebSocket bidirectional proxy
    - SSE/streaming response support
    """
    
    def __init__(
        self,
        upstream: str,
        timeout: int = 600,
        app_name: Optional[str] = None,
        socket_path: Optional[str] = None,
    ) -> None:
        """
        Initialize interceptor.
        
        Args:
            upstream: Upstream service URL (e.g., "http://127.0.0.1:8080")
            timeout: Request timeout in seconds
            app_name: Application name (for logging)
            socket_path: Unix socket path for listening
        """
        self._upstream = upstream.rstrip("/")
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._app_name = app_name or env.app.name
        self._socket_path = socket_path or get_socket_path()
        
        self._session: Optional[aiohttp.ClientSession] = None
    
    @property
    def socket_path(self) -> str:
        """Get socket path"""
        return self._socket_path
    
    async def _on_startup(self, app: web.Application):
        """Startup handler"""
        uvicorn_logger.info(f"{self._app_name} Interceptor starting...")
        uvicorn_logger.info(f"Upstream: {self._upstream}")
        uvicorn_logger.info(f"Socket: {self._socket_path}")
        
        self._session = aiohttp.ClientSession(timeout=self._timeout)
    
    async def _on_shutdown(self, app: web.Application):
        """Shutdown handler"""
        uvicorn_logger.info(f"{self._app_name} Interceptor shutting down...")
        
        if self._session:
            await self._session.close()
        
        if self._socket_path and os.path.exists(self._socket_path):
            try:
                os.remove(self._socket_path)
            except Exception:
                pass
    
    async def _proxy_http(self, request: web.Request) -> web.StreamResponse:
        """Proxy HTTP request"""
        path = request.path
        if request.query_string:
            path = f"{path}?{request.query_string}"
        url = f"{self._upstream}{path}"
        
        headers = {
            k: v for k, v in request.headers.items()
            if k.lower() not in ("host", "connection", "keep-alive", "transfer-encoding")
        }
        
        body = await request.read()
        
        try:
            async with self._session.request(
                method=request.method,
                url=url,
                headers=headers,
                data=body if body else None,
            ) as resp:
                content_type = resp.headers.get("Content-Type", "")
                is_stream = (
                    "text/event-stream" in content_type or
                    "chunked" in resp.headers.get("Transfer-Encoding", "")
                )
                
                resp_headers = {
                    k: v for k, v in resp.headers.items()
                    if k.lower() not in ("transfer-encoding", "connection", "content-encoding", "content-length")
                }
                
                if is_stream:
                    response = web.StreamResponse(status=resp.status, headers=resp_headers)
                    response.content_type = content_type
                    await response.prepare(request)
                    async for chunk in resp.content.iter_any():
                        await response.write(chunk)
                    await response.write_eof()
                    return response
                else:
                    content = await resp.read()
                    return web.Response(
                        body=content,
                        status=resp.status,
                        headers=resp_headers,
                        content_type=content_type or "application/octet-stream",
                    )
        
        except asyncio.TimeoutError:
            return web.Response(text="Gateway Timeout", status=504)
        except aiohttp.ClientError as e:
            uvicorn_logger.error(f"Upstream error: {e}")
            return web.Response(text="Bad Gateway", status=502)
    
    async def _proxy_websocket(self, request: web.Request) -> web.WebSocketResponse:
        """Proxy WebSocket"""
        client_ws = web.WebSocketResponse()
        await client_ws.prepare(request)
        
        ws_url = self._upstream.replace("http://", "ws://").replace("https://", "wss://")
        ws_url = f"{ws_url}{request.path}"
        
        try:
            async with self._session.ws_connect(ws_url) as upstream_ws:
                async def c2u():
                    async for msg in client_ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            await upstream_ws.send_str(msg.data)
                        elif msg.type == aiohttp.WSMsgType.BINARY:
                            await upstream_ws.send_bytes(msg.data)
                        elif msg.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.ERROR):
                            break
                
                async def u2c():
                    async for msg in upstream_ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            await client_ws.send_str(msg.data)
                        elif msg.type == aiohttp.WSMsgType.BINARY:
                            await client_ws.send_bytes(msg.data)
                        elif msg.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.ERROR):
                            break
                
                await asyncio.gather(c2u(), u2c(), return_exceptions=True)
        except Exception as e:
            uvicorn_logger.error(f"WebSocket error: {e}")
        
        return client_ws
    
    async def _handle_request(self, request: web.Request) -> web.StreamResponse:
        """Route handler"""
        if (
            request.headers.get("Upgrade", "").lower() == "websocket" and
            request.headers.get("Connection", "").lower() == "upgrade"
        ):
            return await self._proxy_websocket(request)
        return await self._proxy_http(request)
    
    def serve(self) -> None:
        """Start server (blocking)"""
        app = web.Application()
        app.on_startup.append(self._on_startup)
        app.on_shutdown.append(self._on_shutdown)
        app.router.add_route("*", "/{path:.*}", self._handle_request)
        app.router.add_route("*", "/", self._handle_request)
        
        web.run_app(
            app,
            path=self._socket_path,
            print=lambda *args: None,
        )
    
    async def serve_async(self) -> web.AppRunner:
        """Start server (async, non-blocking)"""
        app = web.Application()
        app.on_startup.append(self._on_startup)
        app.on_shutdown.append(self._on_shutdown)
        app.router.add_route("*", "/{path:.*}", self._handle_request)
        app.router.add_route("*", "/", self._handle_request)
        
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.UnixSite(runner, self._socket_path)
        await site.start()
        
        return runner
