from ..utils.log import uvicorn_logger
from ..config import env
import aiohttp
import asyncio
import requests
from typing import Dict, Any, TypedDict, Optional, Literal
from urllib.parse import quote
import time

# connector type
ConnectorType = Literal["proxy", "brslet"]

# socket configuration (lazy loading)
def _get_socket_paths() -> Dict[ConnectorType, str]:
    return {
        "proxy": env.register.proxy_socket,
        "brslet": env.register.brslet_socket,
    }

# async unix connectors (lazy init)
_CONNECTORS: Dict[ConnectorType, Optional[aiohttp.UnixConnector]] = {
    "proxy": None,
    "brslet": None,
}

# sync session (lazy init)
_SYNC_SESSION: Optional[requests.Session] = None


def _build_unix_url(socket_path: str, api_path: str) -> str:
    """Build requests_unixsocket format Unix socket URL
    
    Args:
        socket_path: socket file path, e.g. /var/run/ieops/proxy.sock
        api_path: API path, e.g. register
        
    Returns:
        http+unix://%2Fvar%2Frun%2Fieops%2Fproxy.sock/register
    """
    encoded_socket = quote(socket_path, safe='')
    return f"http+unix://{encoded_socket}/{api_path}"


class Payload(TypedDict):
    path: str
    payload: Dict[str, Any]

class Response:
    """HTTP response wrapper"""
    def __init__(self, message: str, data: Optional[Any] = None):
        self.message = message
        self.data = data
    
    def __repr__(self) -> str:
        return f"Response(message={self.message!r}, data={self.data!r})"


def _get_connector(connector_type: ConnectorType) -> aiohttp.UnixConnector:
    """Get async Unix socket connector of specified type (lazy loading)"""
    if _CONNECTORS[connector_type] is None:
        socket_paths = _get_socket_paths()
        _CONNECTORS[connector_type] = aiohttp.UnixConnector(path=socket_paths[connector_type])
    return _CONNECTORS[connector_type]


def _get_sync_session() -> requests.Session:
    """Get sync HTTP session with Unix socket support"""
    global _SYNC_SESSION
    if _SYNC_SESSION is None:
        _SYNC_SESSION = requests.Session()
        # Add Unix socket support
        try:
            from requests_unixsocket import UnixAdapter
            _SYNC_SESSION.mount("http+unix://", UnixAdapter())
        except ImportError:
            uvicorn_logger.warning("requests_unixsocket not installed, Unix socket support disabled")
    return _SYNC_SESSION


def post(_payload: Payload, timeout: float = 0.8, max_retries: int = 2, connector_type: ConnectorType = "proxy") -> Response:
    """send POST request via Unix socket
    
    Args:
        _payload: request data
        timeout: timeout in seconds
        max_retries: max retry count
        connector_type: "proxy" or "brslet"
    """
    err = None
    session = _get_sync_session()
    socket_paths = _get_socket_paths()
    url = _build_unix_url(socket_paths[connector_type], _payload['path'])
    for attempt in range(max_retries + 1):
        try:
            resp = session.post(url, json=_payload['payload'], timeout=timeout)
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    return Response(message=data.get('message', ''), data=data.get('data'))
                except ValueError as e:
                    err = Response(message=f"Invalid JSON response: {e}")
            else:
                err = Response(message=f"HTTP {resp.status_code}: {resp.text[:200]}")
        except requests.Timeout as e:
            err = Response(message=f"Client POST [{_payload['path']}] timeout: {e}")
        except requests.RequestException as e:
            err = Response(message=f"Client POST [{_payload['path']}] failed: {e}")
        if attempt < max_retries:
            time.sleep(0.1 * (attempt + 1))
        else:
            uvicorn_logger.warning(f"Client POST [{_payload['path']}] failed after {max_retries + 1} attempts: {err}")
    return err


def get(path: str, timeout: float = 0.8, max_retries: int = 2, connector_type: ConnectorType = "proxy") -> Response:
    """send GET request via Unix socket
    
    Args:
        path: API path
        timeout: timeout in seconds
        max_retries: max retry count
        connector_type: "proxy" or "brslet"
    """
    err = None
    session = _get_sync_session()
    socket_paths = _get_socket_paths()
    url = _build_unix_url(socket_paths[connector_type], path)
    for attempt in range(max_retries + 1):
        try:
            resp = session.get(url, timeout=timeout)
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    return Response(message=data.get('message', ''), data=data.get('data'))
                except ValueError as e:
                    err = Response(message=f"Invalid JSON response: {e}")
            else:
                err = Response(message=f"HTTP {resp.status_code}: {resp.text[:200]}")
        except requests.Timeout as e:
            err = Response(message=f"Client GET [{path}] timeout: {e}")
        except requests.RequestException as e:
            err = Response(message=f"Client GET [{path}] failed: {e}")
        if attempt < max_retries:
            time.sleep(0.1 * (attempt + 1))
        else:
            uvicorn_logger.warning(f"Client GET [{path}] failed after {max_retries + 1} attempts: {err}")
    return err


def delete(path: str, timeout: float = 0.8, max_retries: int = 2, connector_type: ConnectorType = "proxy") -> Response:
    """send DELETE request via Unix socket
    
    Args:
        path: API path
        timeout: timeout in seconds
        max_retries: max retry count
        connector_type: "proxy" or "brslet"
    """
    err = None
    session = _get_sync_session()
    socket_paths = _get_socket_paths()
    url = _build_unix_url(socket_paths[connector_type], path)
    for attempt in range(max_retries + 1):
        try:
            resp = session.delete(url, timeout=timeout)
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    return Response(message=data.get('message', ''), data=data.get('data'))
                except ValueError as e:
                    err = Response(message=f"Invalid JSON response: {e}")
            else:
                err = Response(message=f"HTTP {resp.status_code}: {resp.text[:200]}")
        except requests.Timeout as e:
            err = Response(message=f"Client DELETE [{path}] timeout: {e}")
        except requests.RequestException as e:
            err = Response(message=f"Client DELETE [{path}] failed: {e}")
        if attempt < max_retries:
            time.sleep(0.1 * (attempt + 1))
        else:
            uvicorn_logger.warning(f"Client DELETE [{path}] failed after {max_retries + 1} attempts: {err}")
    return err


async def async_post(_payload: Payload, timeout: float = 0.8, max_retries: int = 2, connector_type: ConnectorType = "proxy") -> Response:
    """async POST request via Unix socket
    
    Args:
        _payload: request data
        timeout: timeout in seconds
        max_retries: max retry count
        connector_type: "proxy" or "brslet"
    """
    err = None
    url = f"http://localhost/{_payload['path']}"  # aiohttp UnixConnector uses localhost
    client_timeout = aiohttp.ClientTimeout(total=timeout)
    
    for attempt in range(max_retries + 1):
        try:
            async with aiohttp.ClientSession(
                connector=_get_connector(connector_type), 
                connector_owner=False,
                timeout=client_timeout
            ) as session:
                async with session.post(url, json=_payload['payload']) as resp:
                    if resp.status == 200:
                        try:
                            data = await resp.json()
                            return Response(message=data.get('message', ''), data=data.get('data'))
                        except (ValueError, aiohttp.ContentTypeError) as e:
                            err = Response(message=f"Invalid JSON response: {e}")
                    else:
                        text = await resp.text()
                        err = Response(message=f"HTTP {resp.status}: {text[:200]}")
        except asyncio.TimeoutError:
            err = Response(message=f"Client POST [{_payload['path']}] timeout")
        except aiohttp.ClientError as e:
            err = Response(message=f"Client POST [{_payload['path']}] failed: {e}")
        except asyncio.CancelledError:
            raise  # Re-raise, let caller handle cancellation
        if attempt < max_retries:
            await asyncio.sleep(0.1 * (attempt + 1))
        else:
            uvicorn_logger.warning(f"Client POST [{_payload['path']}] failed after {max_retries + 1} attempts: {err}")
    return err


async def async_get(path: str, timeout: float = 0.8, max_retries: int = 2, connector_type: ConnectorType = "proxy") -> Response:
    """async GET request via Unix socket
    
    Args:
        path: API path
        timeout: timeout in seconds
        max_retries: max retry count
        connector_type: "proxy" or "brslet"
    """
    err = None
    url = f"http://localhost/{path}"  # aiohttp UnixConnector uses localhost
    client_timeout = aiohttp.ClientTimeout(total=timeout)
    
    for attempt in range(max_retries + 1):
        try:
            async with aiohttp.ClientSession(
                connector=_get_connector(connector_type), 
                connector_owner=False,
                timeout=client_timeout
            ) as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        try:
                            data = await resp.json()
                            return Response(message=data.get('message', ''), data=data.get('data'))
                        except (ValueError, aiohttp.ContentTypeError) as e:
                            err = Response(message=f"Invalid JSON response: {e}")
                    else:
                        text = await resp.text()
                        err = Response(message=f"HTTP {resp.status}: {text[:200]}")
        except asyncio.TimeoutError:
            err = Response(message=f"Client GET [{path}] timeout")
        except aiohttp.ClientError as e:
            err = Response(message=f"Client GET [{path}] failed: {e}")
        except asyncio.CancelledError:
            raise  # Re-raise, let caller handle cancellation
        if attempt < max_retries:
            await asyncio.sleep(0.1 * (attempt + 1))
        else:
            uvicorn_logger.warning(f"Client GET [{path}] failed after {max_retries + 1} attempts: {err}")
    return err


async def async_delete(path: str, timeout: float = 0.8, max_retries: int = 2, connector_type: ConnectorType = "proxy") -> Response:
    """async DELETE request via Unix socket
    
    Args:
        path: API path
        timeout: timeout in seconds
        max_retries: max retry count
        connector_type: "proxy" or "brslet"
    """
    err = None
    url = f"http://localhost/{path}"  # aiohttp UnixConnector uses localhost
    client_timeout = aiohttp.ClientTimeout(total=timeout)
    
    for attempt in range(max_retries + 1):
        try:
            async with aiohttp.ClientSession(
                connector=_get_connector(connector_type), 
                connector_owner=False,
                timeout=client_timeout
            ) as session:
                async with session.delete(url) as resp:
                    if resp.status == 200:
                        try:
                            data = await resp.json()
                            return Response(message=data.get('message', ''), data=data.get('data'))
                        except (ValueError, aiohttp.ContentTypeError) as e:
                            err = Response(message=f"Invalid JSON response: {e}")
                    else:
                        text = await resp.text()
                        err = Response(message=f"HTTP {resp.status}: {text[:200]}")
        except asyncio.TimeoutError:
            err = Response(message=f"Client DELETE [{path}] timeout")
        except aiohttp.ClientError as e:
            err = Response(message=f"Client DELETE [{path}] failed: {e}")
        except asyncio.CancelledError:
            raise  # Re-raise, let caller handle cancellation
        if attempt < max_retries:
            await asyncio.sleep(0.1 * (attempt + 1))
        else:
            uvicorn_logger.warning(f"Client DELETE [{path}] failed after {max_retries + 1} attempts: {err}")
    return err
