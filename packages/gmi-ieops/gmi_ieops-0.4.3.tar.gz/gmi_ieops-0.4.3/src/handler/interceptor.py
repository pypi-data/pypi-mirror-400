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
from typing import Optional, Set

import aiohttp
from aiohttp import web

from ..utils.log import uvicorn_logger
from ..utils.util import get_socket_path
from ..config import env

# Default headers to filter when proxying requests (client -> upstream)
DEFAULT_FILTER_HEADERS = frozenset({
    "host",
    "connection",
    "keep-alive",
    "transfer-encoding",
    "origin",
    "referer",
})

# Default headers to filter when proxying responses (upstream -> client)
DEFAULT_FILTER_RESPONSE_HEADERS = frozenset({
    "transfer-encoding",
    "connection",
    "content-encoding",
    "content-length",
    "content-type",  # handled separately via content_type/charset params
})


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
        filter_headers: Optional[Set[str]] = None,
        filter_response_headers: Optional[Set[str]] = None,
    ) -> None:
        """
        Initialize interceptor.
        
        Args:
            upstream: Upstream service URL (e.g., "http://127.0.0.1:8080")
            timeout: Request timeout in seconds
            app_name: Application name (for logging)
            socket_path: Unix socket path for listening
            filter_headers: Set of header names (lowercase) to filter from requests.
                           Defaults to DEFAULT_FILTER_HEADERS.
            filter_response_headers: Set of header names (lowercase) to filter from responses.
                           Defaults to DEFAULT_FILTER_RESPONSE_HEADERS.
        """
        self._upstream = upstream.rstrip("/")
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._app_name = app_name or env.app.name
        self._socket_path = socket_path or get_socket_path()
        self._filter_headers = filter_headers if filter_headers is not None else DEFAULT_FILTER_HEADERS
        self._filter_response_headers = filter_response_headers if filter_response_headers is not None else DEFAULT_FILTER_RESPONSE_HEADERS
        
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
        # Use path_qs to preserve URL encoding (e.g., gmifs%3A%2F%2F stays encoded)
        # request.path would decode it to gmifs:// which breaks routing
        url = f"{self._upstream}{request.path_qs}"
        
        # Filter out headers that shouldn't be forwarded
        headers = {
            k: v for k, v in request.headers.items()
            if k.lower() not in self._filter_headers
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
                
                # Filter response headers
                resp_headers = {
                    k: v for k, v in resp.headers.items()
                    if k.lower() not in self._filter_response_headers
                }
                
                # Parse content_type to separate charset
                # aiohttp doesn't allow charset in content_type argument
                parsed_content_type = content_type or "application/octet-stream"
                charset = None
                if "; charset=" in parsed_content_type:
                    parts = parsed_content_type.split("; charset=")
                    parsed_content_type = parts[0]
                    charset = parts[1].strip()
                
                if is_stream:
                    response = web.StreamResponse(status=resp.status, headers=resp_headers)
                    response.content_type = parsed_content_type
                    if charset:
                        response.charset = charset
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
                        content_type=parsed_content_type,
                        charset=charset,
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
