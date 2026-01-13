"""
Configuration Module

Provides environment variable management with type-safe access.

Usage:
```python
from gmi_ieops.config import env

# Access grouped configurations
app_name = env.app.name
timeout = env.model.timeout
port = env.server.port

# Or directly get environment variables
value = env.get("MY_ENV_VAR", default="default_value")
value_int = env.get_int("MY_INT_VAR", default=10)
value_bool = env.get_bool("MY_BOOL_VAR", default=False)
```
"""

from .env import (
    env,
    Env,
    EnvVar,
    EnvGroup,
    AppEnv,
    LogEnv,
    ServerEnv,
    ModelEnv,
    DeviceEnv,
    ApiEnv,
    StorageEnv,
    RegisterEnv,
    SSLEnv,
)
from ..utils.util import get_socket_path


__all__ = [
    'env',
    'Env',
    'EnvVar',
    'EnvGroup',
    'AppEnv',
    'LogEnv',
    'ServerEnv',
    'ModelEnv',
    'DeviceEnv',
    'ApiEnv',
    'StorageEnv',
    'RegisterEnv',
    'SSLEnv',
    'get_socket_path',
]
