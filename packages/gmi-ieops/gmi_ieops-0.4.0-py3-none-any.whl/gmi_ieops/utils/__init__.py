"""
Utils Module - Provides common utility functions
"""

# Logging
from .log import log, uvicorn_logger

# Import env for internal use (logger initialization)
from ..config import env as _env

# Random utilities and path helpers
from .util import randstr, arandstr, randint, arandint, APP_ID, get_socket_path

# File operations
from .file import load_json, save_json, save, save_jfs

# Subprocess management
from .subprocess_manager import SubprocessManager, create_http_health_check

# LLM sampling params (import as module)
from . import llm_sampling_params

# Initialize logger with environment variables
log.set_logger(
    log_path=_env.log.path,
    app_name=_env.app.name,
    log_level=_env.log.level,
    file_enabled=_env.log.file_enabled,
)

__all__ = [
    # Logging
    'log',
    'uvicorn_logger',
    
    # Random utilities and path helpers
    'randstr',
    'arandstr',
    'randint',
    'arandint',
    'APP_ID',
    'get_socket_path',
    
    # File operations
    'load_json',
    'save_json',
    'save',
    'save_jfs',
    
    # Subprocess management
    'SubprocessManager',
    'create_http_health_check',
    
    # LLM sampling params
    'llm_sampling_params',
]
