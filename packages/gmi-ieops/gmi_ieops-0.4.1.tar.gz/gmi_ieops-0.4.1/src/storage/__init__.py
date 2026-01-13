"""
Storage Module - User-isolated Distributed File System Access

NOTE: NFS support has been DISABLED. Only WebDAV backend is available.
Set IEOPS_WEBDAV_URL environment variable to configure storage.

=== Unified FileSystem API (Recommended) ===

FileSystem uses WebDAV backend:

    from gmi_ieops.storage import FileSystem
    
    # Auto-select backend based on env vars (WebDAV only now)
    fs = FileSystem()
    
    # Or explicit backend
    fs = FileSystem(backend="webdav", hostname="http://10.0.0.1:5000")
    
    with fs.open("data.txt", "w") as f:
        f.write("Hello Storage")

=== Protocol Prefix (for open() interception) ===

Use gmifs:// prefix with standard open(), backend auto-selected by env vars:

    from gmi_ieops.storage import enable_storage_intercept
    enable_storage_intercept()  # Auto-enable based on env vars
    
    # Write to remote storage (WebDAV)
    with open("gmifs://output/image.png", "wb") as f:
        f.write(image_data)
    
    # Local files unchanged
    with open("/tmp/local.txt", "w") as f:
        f.write("local")
"""

import builtins
import os
from typing import Optional

from .filesystem import (
    # High-level API (WebDAV only, NFS support disabled)
    FileSystem,
    # Module availability checks (NFS disabled)
    # _ensure_nfs_module,  # DISABLED - NFS support removed
    _ensure_webdav_module,
    # _get_nfs_class,  # DISABLED - NFS support removed
    _get_webdav_class,
    # Path utilities
    _get_base_path,
    _create_safe_path,
)

from ..config import env


# ============================================================================
# Protocol Interception - gmifs:// routes to WebDAV or NFS based on config
# ============================================================================

# Protocol constant
GMIFS_PROTOCOL = "gmifs://"

# Global state
_global_fs = None  # FileSystem instance (WebDAV only, NFS disabled)
_fs_init_error = None
_builtin_open = builtins.open
_current_backend = None  # 'webdav' or None (NFS disabled)


def _intercepted_open(file, mode='r', buffering=-1, encoding=None,
                      errors=None, newline=None, closefd=True, opener=None):
    """
    Intercepted open function - routes gmifs:// paths to storage backend
    
    Backend: WebDAV only (NFS support disabled)
    - IEOPS_WEBDAV_URL -> WebDAV
    
    Examples:
        open("gmifs://output/image.png", "wb")  -> Remote storage (WebDAV)
        open("/data/local/file.txt", "w")       -> Local (default)
    """
    global _global_fs
    
    file_str = str(file)
    
    # Check for gmifs:// protocol prefix
    if file_str.startswith(GMIFS_PROTOCOL):
        # Extract path after gmifs://
        rel_path = file_str[len(GMIFS_PROTOCOL):]
        
        if _global_fs is None:
            if _fs_init_error:
                raise IOError(f"Cannot open '{file_str}': Storage initialization failed - {_fs_init_error}")
            else:
                raise IOError(f"Cannot open '{file_str}': Storage not configured (set IEOPS_WEBDAV_URL or IEOPS_NFS_SERVER)")
        
        try:
            return _global_fs.open(rel_path, mode, encoding)
        except Exception as e:
            raise IOError(f"Failed to open storage file '{rel_path}': {e}")
    
    # No gmifs:// prefix - use native open
    return _builtin_open(file, mode, buffering, encoding, errors, newline, closefd, opener)


def enable_storage_intercept(
    backend: str = "auto",
    # WebDAV options
    hostname: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    # NFS options (DISABLED)
    server: Optional[str] = None,  # IGNORED - NFS support disabled
    port: Optional[int] = None,    # IGNORED - NFS support disabled
) -> str:
    """
    Enable gmifs:// protocol support for open()
    
    NOTE: NFS support has been DISABLED. Only WebDAV backend is available.
    Set IEOPS_WEBDAV_URL environment variable to configure storage.
    
    After calling this, you can use gmifs:// prefix:
        open("gmifs://output/image.png", "wb")  -> Remote storage (WebDAV)
        open("/local/file.txt", "w")            -> Local filesystem (unchanged)
    
    Args:
        backend: "auto" or "webdav" (NFS disabled)
        hostname: WebDAV server URL (or use IEOPS_WEBDAV_URL env)
        username: WebDAV username (or use IEOPS_WEBDAV_USER env)
        password: WebDAV password (or use IEOPS_WEBDAV_PASS env)
        server: IGNORED - NFS support disabled
        port: IGNORED - NFS support disabled
        
    Returns:
        'webdav' or 'none'
    """
    global _global_fs, _fs_init_error, _current_backend
    
    # Clean up previous instance
    if _global_fs is not None:
        try:
            _global_fs.close()
        except Exception:
            pass
        _global_fs = None
    
    _fs_init_error = None
    _current_backend = None
    
    try:
        # Determine backend (NFS disabled, WebDAV only)
        if backend == "auto":
            # NFS support disabled - ignore NFS env vars
            # if server or env.storage.nfs_server:
            #     backend = "nfs"
            if hostname or env.storage.webdav_url:
                backend = "webdav"
            else:
                builtins.open = _intercepted_open  # Register for error messages
                return 'none'
        
        # Initialize FileSystem with specified backend
        if backend == "webdav":
            _global_fs = FileSystem(
                backend="webdav",
                hostname=hostname,
                username=username,
                password=password,
                auto_mkdir=True
            )
            _current_backend = 'webdav'
        elif backend == "nfs":
            # NFS support disabled
            raise ValueError("NFS backend has been disabled. Use WebDAV instead (set IEOPS_WEBDAV_URL).")
        else:
            raise ValueError(f"Unknown backend: {backend}")
        
        builtins.open = _intercepted_open
        return _current_backend
        
    except Exception as e:
        _fs_init_error = str(e)
        builtins.open = _intercepted_open  # Register for error messages
        return 'none'


def disable_storage_intercept():
    """Disable gmifs:// open() interception"""
    global _global_fs, _current_backend
    
    builtins.open = _builtin_open
    
    if _global_fs is not None:
        try:
            _global_fs.close()
        except Exception:
            pass
        _global_fs = None
    
    _current_backend = None


def get_storage_backend() -> Optional[str]:
    """Get current storage backend type: 'webdav' or None (NFS disabled)"""
    return _current_backend


# Legacy aliases for backward compatibility
def enable_nfs_intercept() -> bool:
    """Legacy: NFS backend DISABLED. Use enable_storage_intercept(backend='webdav') instead."""
    # NFS support disabled - return False
    return False


def disable_nfs_intercept():
    """Legacy: Disable interception. Use disable_storage_intercept() instead."""
    disable_storage_intercept()


# ============================================================================
# Auto-enable if configured
# ============================================================================

def _auto_enable():
    """Auto-enable storage interception if env vars are configured (WebDAV only)"""
    # NFS support disabled - only check WebDAV env var
    if env.storage.webdav_url:
        try:
            enable_storage_intercept()
        except Exception as e:
            global _fs_init_error
            _fs_init_error = str(e)
            builtins.open = _intercepted_open

_auto_enable()


# ============================================================================
# Lazy Loading for Optional Dependencies
# ============================================================================

def __getattr__(name):
    """Lazy load classes to avoid crashes when dependencies are not installed"""
    # NFS classes - DISABLED
    if name in ('NFSFile', 'FileStat', 'DirEntry', 'NFSError', 'NFSLockError'):
        raise ImportError(f"NFS support has been disabled. Class '{name}' is not available. Use WebDAV backend instead.")
    
    # WebDAV classes
    if name in ('WebDAVFileSystem', 'WebDAVFile', 'WebDAVClient', 'WebDAVError', 'WebDAVLockError'):
        return _get_webdav_class(name)
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # High-level unified API
    'FileSystem',
    # WebDAV-specific classes (lazy loaded)
    'WebDAVFileSystem',
    'WebDAVFile',
    'WebDAVClient',
    # Protocol constant
    'GMIFS_PROTOCOL',
    # Data types - NFS DISABLED
    # 'NFSFile',  # DISABLED - NFS support removed
    # 'FileStat',  # DISABLED - NFS support removed
    # 'DirEntry',  # DISABLED - NFS support removed
    # Exception classes (WebDAV only, NFS disabled)
    # 'NFSError',  # DISABLED - NFS support removed
    # 'NFSLockError',  # DISABLED - NFS support removed
    'WebDAVError',
    'WebDAVLockError',
    # Interception control
    'enable_storage_intercept',
    'disable_storage_intercept',
    'get_storage_backend',
    # Legacy (backward compatibility) - NFS functions disabled but kept for compatibility
    'enable_nfs_intercept',
    'disable_nfs_intercept',
]
