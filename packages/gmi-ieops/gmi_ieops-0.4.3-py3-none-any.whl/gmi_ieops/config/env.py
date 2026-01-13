"""
Environment Variable Manager

Provides type-safe environment variable access with support for:
- Automatic type conversion (str, int, float, bool, list)
- Default value management
- Environment variable grouping
- Lazy loading (read on first access)

Usage:
```python
from gmi_ieops.config import env

# Access environment variables
app_name = env.app.name
timeout = env.model.timeout
port = env.server.port

# Or directly get environment variables
value = env.get("MY_ENV_VAR", default="default_value")
value_int = env.get_int("MY_INT_VAR", default=10)
value_bool = env.get_bool("MY_BOOL_VAR", default=False)
```
"""

import os
from typing import Any, Dict, List, Optional, TypeVar, Union


T = TypeVar('T')


class EnvVar:
    """Environment variable descriptor with lazy loading and type conversion"""
    
    def __init__(
        self, 
        name: str, 
        default: Any = None, 
        type_: type = str,
        description: str = ""
    ):
        self.name = name
        self.default = default
        self.type_ = type_
        self.description = description
        self._value: Any = None
        self._loaded = False
        self._is_set = False  # Whether environment variable is set
    
    def __get__(self, obj: Any, objtype: Any = None) -> Any:
        """Descriptor protocol - return value when accessed from instance"""
        if obj is None:
            return self  # Accessed from class, return descriptor itself
        return self.get()
    
    def _convert(self, value: str) -> Any:
        """Type conversion"""
        if self.type_ == bool:
            return value.lower() in ('true', '1', 'yes', 'on')
        elif self.type_ == int:
            return int(value)
        elif self.type_ == float:
            return float(value)
        elif self.type_ == list:
            return [v.strip() for v in value.split(',') if v.strip()]
        return value
    
    def get(self) -> Any:
        """Get value (lazy loading)"""
        if not self._loaded:
            raw = os.environ.get(self.name)
            if raw is not None:
                self._value = self._convert(raw)
                self._is_set = True
            else:
                self._value = self.default
                self._is_set = False
            self._loaded = True
        return self._value
    
    @property
    def is_set(self) -> bool:
        """Check if environment variable is explicitly set (even if empty)"""
        if not self._loaded:
            self.get()  # Trigger loading
        return self._is_set
    
    def reload(self) -> Any:
        """Reload value"""
        self._loaded = False
        self._is_set = False
        return self.get()


class EnvGroup:
    """Environment variable group base class"""
    
    def __init__(self):
        self._vars: Dict[str, EnvVar] = {}
        # Auto-collect all EnvVar attributes
        for name in dir(self.__class__):
            attr = getattr(self.__class__, name)
            if isinstance(attr, EnvVar):
                self._vars[name] = attr
    
    def __getattribute__(self, name: str) -> Any:
        # Avoid recursion
        if name.startswith('_') or name in ('reload', 'to_dict', 'get_var', 'is_set'):
            return super().__getattribute__(name)
        
        try:
            vars_dict = super().__getattribute__('_vars')
            if name in vars_dict:
                return vars_dict[name].get()
        except AttributeError:
            pass
        
        return super().__getattribute__(name)
    
    def reload(self) -> None:
        """Reload all configurations"""
        for var in self._vars.values():
            var.reload()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {name: var.get() for name, var in self._vars.items()}
    
    def get_var(self, name: str) -> Optional[EnvVar]:
        """Get environment variable descriptor"""
        return self._vars.get(name)
    
    def is_set(self, name: str) -> bool:
        """Check if environment variable is explicitly set"""
        var = self._vars.get(name)
        return var.is_set if var else False


# ========== Environment Variable Group Definitions ==========

class AppEnv(EnvGroup):
    """Application environment variables"""
    name = EnvVar("APP_NAME", "ieops", str, "Application name")
    

class LogEnv(EnvGroup):
    """Logging environment variables"""
    path = EnvVar("LOG_FILE_PATH", "/var/log/ieops", str, "Log file path")
    level = EnvVar("LOG_LEVEL", "INFO", str, "Log level")
    file_enabled = EnvVar("LOG_FILE_ENABLED", False, bool, "Enable file logging")


class ServerEnv(EnvGroup):
    """Server environment variables
    
    Server mode selection:
    - If MODEL_SERVER_PORT is set (> 0): Use TCP mode (host:port)
    - If MODEL_SERVER_PORT is not set or 0: Use Unix socket mode
    """
    socket_dir = EnvVar("MODEL_SERVER_SOCKET_DIR", "", str, "Unix socket directory (empty = current directory)")
    host = EnvVar("MODEL_SERVER_HOST", "127.0.0.1", str, "Listen address (TCP mode)")
    port = EnvVar("MODEL_SERVER_PORT", 0, int, "Listen port (0 = use socket mode)")
    graceful_shutdown_time = EnvVar("GRACEFUL_SHUTDOWN_TIME", 3, int, "Graceful shutdown timeout (seconds)")


class ModelEnv(EnvGroup):
    """Model environment variables"""
    path = EnvVar("MODEL_PATH", "", str, "Model path")
    name = EnvVar("MODEL_NAME", "model", str, "Model name")
    timeout = EnvVar("MODEL_TIMEOUT", 600, int, "Inference timeout (seconds)")
    concurrency = EnvVar("MODEL_THREAD_CONCURRENCY", 8, int, "Concurrency")
    tensor_parallel_size = EnvVar("TENSOR_PARALLEL_SIZE", 1, int, "Tensor parallel size")
    infer_engine = EnvVar("MODEL_INFER_ENGINE", "vllm", str, "Inference engine")
    tokenizer_name = EnvVar("TOKENIZER_NAME", "transformers", str, "Tokenizer type")


class DeviceEnv(EnvGroup):
    """Device environment variables"""
    cuda_visible = EnvVar("CUDA_VISIBLE_DEVICES", "0", str, "Visible GPU devices")
    device = EnvVar("DEVICE", "auto", str, "Compute device (cuda/cpu/auto)")
    torch_dtype = EnvVar("TORCH_DTYPE", "float16", str, "PyTorch data type")
    cuda_home = EnvVar("CUDA_HOME", "/usr/local/cuda", str, "CUDA installation path")
    ld_library_path = EnvVar("LD_LIBRARY_PATH", "", str, "Library search path")


class ApiEnv(EnvGroup):
    """API environment variables"""
    gmi_api_key = EnvVar("GMI_API_KEY", "", str, "GMI API key")


class StorageEnv(EnvGroup):
    """Storage environment variables
    
    Supports two backends:
    1. NFS (via libnfs) - High performance, requires libnfs-dev
    2. WebDAV (via webdavclient3) - No special deps, works in unprivileged containers
    
    Note: Linux NFS kernel has a max block size of 1MB (1,048,576 bytes).
    Default chunk sizes are set to 512KB for safety margin.
    """
    # Common storage settings (user isolation)
    pid = EnvVar("IEOPS_STORAGE_PID", "u-00000000", str, "Storage PID")
    fs_name = EnvVar("IEOPS_STORAGE_FS_NAME", "jfs-dev", str, "Filesystem name")
    oid = EnvVar("IEOPS_STORAGE_OID", "gmicloud.ieops", str, "Organization ID")
    uid = EnvVar("IEOPS_STORAGE_UID", "gmicloud.ieops", str, "User ID")
    
    # NFS settings
    nfs_server = EnvVar("IEOPS_NFS_SERVER", "", str, "NFS server address (e.g., 10.0.0.1:32049)")
    write_chunk_size = EnvVar("IEOPS_NFS_WRITE_CHUNK_SIZE", 512 * 1024, int, "NFS write chunk size in bytes (default 512KB, max 1MB)")
    read_chunk_size = EnvVar("IEOPS_NFS_READ_CHUNK_SIZE", 512 * 1024, int, "NFS read chunk size in bytes (default 512KB, max 1MB)")
    timeout = EnvVar("IEOPS_NFS_TIMEOUT", 30000, int, "NFS timeout in milliseconds (default 30s)")
    
    # WebDAV settings
    webdav_url = EnvVar("IEOPS_WEBDAV_URL", "", str, "WebDAV server URL (e.g., http://10.0.0.1:5000)")
    webdav_user = EnvVar("IEOPS_WEBDAV_USER", "", str, "WebDAV username")
    webdav_pass = EnvVar("IEOPS_WEBDAV_PASS", "", str, "WebDAV password")
    webdav_timeout = EnvVar("IEOPS_WEBDAV_TIMEOUT", 30, int, "WebDAV timeout in seconds (default 30s)")


class RegisterEnv(EnvGroup):
    """Registration environment variables"""
    enabled = EnvVar("REGISTER_ENABLED", True, bool, "Enable registration")
    interval = EnvVar("REGISTER_INTERVAL", 10, int, "Registration interval (seconds)")
    proxy_socket = EnvVar("IEOPS_PROXY_SOCKET", "/var/run/ieops/proxy.sock", str, "Proxy socket")
    brslet_socket = EnvVar("IEOPS_BRSLET_SOCKET", "/var/run/ieops/brslet.sock", str, "Brslet socket")


class SSLEnv(EnvGroup):
    """SSL/TLS environment variables"""
    cert_file = EnvVar("SSL_CERT_FILE", "", str, "SSL certificate file path")
    cert_dir = EnvVar("SSL_CERT_DIR", "", str, "SSL certificate directory")
    requests_ca_bundle = EnvVar("REQUESTS_CA_BUNDLE", "", str, "CA bundle for requests library")


# ========== Main Environment Variable Manager ==========

class Env:
    """
    Unified Environment Variable Manager
    
    Usage:
    ```python
    from gmi_ieops.config import env
    
    # Access grouped configurations
    print(env.app.name)
    print(env.server.port)
    print(env.model.timeout)
    
    # Get environment variables directly
    value = env.get("MY_VAR", "default")
    value_int = env.get_int("MY_INT", 10)
    value_bool = env.get_bool("MY_BOOL", False)
    
    # Reload configurations
    env.reload()
    ```
    """
    
    def __init__(self):
        self.app = AppEnv()
        self.log = LogEnv()
        self.server = ServerEnv()
        self.model = ModelEnv()
        self.device = DeviceEnv()
        self.api = ApiEnv()
        self.storage = StorageEnv()
        self.register = RegisterEnv()
        self.ssl = SSLEnv()
    
    def get(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """Get string environment variable"""
        return os.environ.get(name, default)
    
    def get_int(self, name: str, default: int = 0) -> int:
        """Get integer environment variable"""
        value = os.environ.get(name)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default
    
    def get_float(self, name: str, default: float = 0.0) -> float:
        """Get float environment variable"""
        value = os.environ.get(name)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            return default
    
    def get_bool(self, name: str, default: bool = False) -> bool:
        """Get boolean environment variable"""
        value = os.environ.get(name)
        if value is None:
            return default
        return value.lower() in ('true', '1', 'yes', 'on')
    
    def get_list(self, name: str, default: Optional[List[str]] = None, sep: str = ',') -> List[str]:
        """Get list environment variable"""
        value = os.environ.get(name)
        if value is None:
            return default or []
        return [v.strip() for v in value.split(sep) if v.strip()]
    
    def reload(self) -> None:
        """Reload all configurations"""
        self.app.reload()
        self.log.reload()
        self.server.reload()
        self.model.reload()
        self.device.reload()
        self.api.reload()
        self.storage.reload()
        self.register.reload()
        self.ssl.reload()
    
    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        """Convert to dictionary"""
        return {
            "app": self.app.to_dict(),
            "log": self.log.to_dict(),
            "server": self.server.to_dict(),
            "model": self.model.to_dict(),
            "device": self.device.to_dict(),
            "api": self.api.to_dict(),
            "storage": self.storage.to_dict(),
            "register": self.register.to_dict(),
            "ssl": self.ssl.to_dict(),
        }
    
    def get_socket_path(self, socket_dir: str = None) -> str:
        """Get socket file path (convenience method)"""
        from ..utils.util import get_socket_path as _get_socket_path
        return _get_socket_path(socket_dir)


# Global environment variable instance
env = Env()

