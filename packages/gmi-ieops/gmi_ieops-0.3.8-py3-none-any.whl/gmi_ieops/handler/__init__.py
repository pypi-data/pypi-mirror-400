"""
Handler Module - Provides inference server and handlers

Usage:
```python
from gmi_ieops.handler import Handler, Server, RouterDef, RouterKind

server = Server(
    routers={
        "chat": [
            RouterDef(path="stream", handler=model.chat, kind=RouterKind.SSE),
            RouterDef(path="complete", handler=model.complete, kind=RouterKind.API),
        ],
    },
)
Handler(server=server).serve()
```

NFS Storage Integration:
    When IEOPS_NFS_SERVER environment variable is set, importing this module
    automatically enables NFS storage interception. This allows using `gmifs://`
    protocol prefix in standard `open()` calls:
    
    ```python
    # Write to NFS (if IEOPS_NFS_SERVER is configured)
    with open("gmifs://output/image.png", "wb") as f:
        f.write(image_data)
    
    # Local file access is unaffected
    with open("/data/local/file.txt", "r") as f:
        data = f.read()
    ```
"""

import os

from .handler import Handler

# Auto-enable NFS storage interception if IEOPS_NFS_SERVER is configured
# This allows using gmifs:// protocol in open() calls without explicit import
if os.environ.get("IEOPS_NFS_SERVER"):
    try:
        import gmi_ieops.storage  # noqa: F401
    except (ImportError, OSError) as e:
        # libnfs not installed or failed to load
        # The storage module will register a fallback interceptor that provides clear error messages
        pass
from .tokenizer import TokenizerPool, TokenizerBase

# Server
from .server import Server, UnifiedServer

# Router core types
from .router import (
    RouterDef,
    RouterConfig,
    RouterKind,
    HTTPMethod,
    generate_trace_id,
    format_error_response,
    # Status codes (for special scenarios like comfyui)
    SERVER_CODE_OK,
    SERVER_CODE_ERROR,
    SERVER_CODE_STOP,
)

__all__ = [
    # Core
    'Handler',
    'Server',
    
    # Router definitions
    'RouterDef',
    'RouterConfig',
    'RouterKind',
    'HTTPMethod',
    
    # Utilities
    'generate_trace_id',
    'format_error_response',
    
    # Status codes
    'SERVER_CODE_OK',
    'SERVER_CODE_ERROR',
    'SERVER_CODE_STOP',
    
    # Tokenizer (needed by specific workers)
    'TokenizerPool',
    'TokenizerBase',
]
