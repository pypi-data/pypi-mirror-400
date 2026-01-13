import random
import os

_TOKEN_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


async def arandstr(n: int):
    return ''.join(random.choices(_TOKEN_CHARS, k=n))


async def arandint(a, b):
    return int(random.random()*(b-a))+a


def randstr(n: int):
    return ''.join(random.choices(_TOKEN_CHARS, k=n))


def randint(a, b):
    return int(random.random()*(b-a))+a


APP_ID = f"{os.getenv('APP_NAME', 'ieops')}.{randstr(8)}"


def get_socket_path(socket_dir: str = None) -> str:
    """
    Get Unix socket file path.
    
    Path format: {socket_dir}/{APP_ID}.sock
    
    Args:
        socket_dir: Socket directory path. If None, uses MODEL_SERVER_SOCKET_DIR env var.
                   If empty string, uses current working directory.
    
    Returns:
        Full socket file path (e.g., "/var/run/ieops/comfyui-worker.abc123.sock")
    
    Example:
        >>> from gmi_ieops.utils import get_socket_path
        >>> get_socket_path()  # Uses env var or cwd
        '/current/dir/myapp.abc12345.sock'
        >>> get_socket_path("/var/run/ieops")
        '/var/run/ieops/myapp.abc12345.sock'
    """
    # Determine socket directory
    if socket_dir is None:
        # Lazy import to avoid circular dependency
        from ..config import env
        socket_dir = env.server.socket_dir
    
    # Empty string means current directory
    if not socket_dir:
        socket_dir = os.getcwd()
    
    return os.path.join(socket_dir, f"{APP_ID}.sock")
