"""
WebDAV Storage Client - User-isolated Distributed File System Access

Based on webdavclient3 library, provides:
- User directory isolation (pid/fs_name/oid/uid)
- File operations via HTTP/WebDAV protocol
- No kernel mount required (works in unprivileged containers)
"""

import os
import io
from typing import Optional, List, Generator, Union
from contextlib import contextmanager
from dataclasses import dataclass


# ============================================================================
# Exception Classes
# ============================================================================

class WebDAVError(Exception):
    """WebDAV operation error"""
    pass


class WebDAVLockError(WebDAVError):
    """WebDAV lock error"""
    pass


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class FileStat:
    """File status information"""
    size: int
    mtime: float
    is_dir: bool
    name: str
    path: str
    
    @property
    def is_file(self) -> bool:
        return not self.is_dir


@dataclass 
class DirEntry:
    """Directory entry"""
    name: str
    path: str
    is_dir: bool
    size: int


# ============================================================================
# WebDAV Client Wrapper
# ============================================================================

class WebDAVClient:
    """
    Low-level WebDAV client wrapper
    
    Wraps webdavclient3 with additional features:
    - Automatic retry on connection errors
    - Lock support
    - Stream upload/download
    """
    
    def __init__(self, hostname: str, username: Optional[str] = None, 
                 password: Optional[str] = None, timeout: int = 30):
        """
        Initialize WebDAV client
        
        Args:
            hostname: WebDAV server URL (e.g., "http://10.0.0.1:5000" or "10.0.0.1:5000")
            username: Username for authentication (optional)
            password: Password for authentication (optional)
            timeout: Connection timeout in seconds
        """
        try:
            from webdav3.client import Client
        except ImportError:
            raise ImportError("webdavclient3 not installed. Run: pip install webdavclient3")
        
        # Ensure hostname has a protocol scheme
        hostname = hostname.rstrip('/')
        if not hostname.startswith(('http://', 'https://')):
            hostname = f'http://{hostname}'
        
        options = {
            'webdav_hostname': hostname,
            'webdav_timeout': timeout,
            # Disable HEAD requests - some WebDAV servers don't support HEAD method
            # This prevents MethodNotSupported errors during mkdir/check operations
            'disable_check': True,
        }
        
        if username:
            options['webdav_login'] = username
        if password:
            options['webdav_password'] = password
            
        self._client = Client(options)
        self._hostname = hostname
    
    # ============ File Operations ============
    
    def upload(self, remote_path: str, local_path: str):
        """Upload local file to remote"""
        # Use direct PUT request to avoid webdavclient3's internal check() calls
        # which fail on servers that don't support HEAD method
        with open(local_path, 'rb') as f:
            self.upload_bytes(remote_path, f.read())
    
    def upload_bytes(self, remote_path: str, data: bytes):
        """Upload bytes to remote file"""
        # Use direct PUT request to avoid webdavclient3's internal check() calls
        # which fail on servers that don't support HEAD method
        from webdav3.urn import Urn
        urn = Urn(remote_path)
        buffer = io.BytesIO(data)
        self._client.execute_request(action='upload', path=urn.quote(), data=buffer)
    
    def download(self, remote_path: str, local_path: str):
        """Download remote file to local"""
        self._client.download_sync(remote_path=remote_path, local_path=local_path)
    
    def download_bytes(self, remote_path: str) -> bytes:
        """Download remote file as bytes"""
        buffer = io.BytesIO()
        self._client.download_from(buffer, remote_path=remote_path)
        return buffer.getvalue()
    
    def read_text(self, remote_path: str, encoding: str = 'utf-8') -> str:
        """Read remote file as text"""
        data = self.download_bytes(remote_path)
        return data.decode(encoding)
    
    def write_text(self, remote_path: str, content: str, encoding: str = 'utf-8'):
        """Write text to remote file"""
        self.upload_bytes(remote_path, content.encode(encoding))
    
    # ============ Directory Operations ============
    
    def mkdir(self, path: str, parents: bool = False):
        """Create directory"""
        if parents:
            # Create parent directories recursively
            parts = path.strip('/').split('/')
            current = ""
            for part in parts:
                current = current + "/" + part
                try:
                    self._client.mkdir(current)
                except Exception:
                    # Only ignore if directory actually exists now
                    # (could be race condition or already existed)
                    if not self.isdir(current):
                        raise
        else:
            self._client.mkdir(path)
    
    def rmdir(self, path: str):
        """Remove directory (must be empty)"""
        self._client.clean(path)
    
    def listdir(self, path: str = "/") -> List[str]:
        """List directory contents (names only)"""
        items = self._client.list(path)
        # Filter out the path itself and clean up names
        return [item.rstrip('/') for item in items if item and item.rstrip('/') != path.rstrip('/').split('/')[-1]]
    
    def scandir(self, path: str = "/") -> List[DirEntry]:
        """List directory with details"""
        entries = []
        for item in self._client.list(path, get_info=True):
            if not item.get('path'):
                continue
            item_path = item['path'].rstrip('/')
            name = item_path.split('/')[-1]
            if not name or item_path == path.rstrip('/'):
                continue
            
            # Parse size (may be string, None, or int)
            size_val = item.get('size')
            if size_val is None:
                size = 0
            elif isinstance(size_val, str):
                size = int(size_val) if size_val.isdigit() else 0
            else:
                size = int(size_val)
            
            # Check isdir
            is_dir = item.get('isdir', False)
            if not isinstance(is_dir, bool):
                # Heuristic: directories have no content_type and size is None
                is_dir = item.get('content_type') is None and item.get('size') is None
            
            entries.append(DirEntry(
                name=name,
                path=item_path,
                is_dir=is_dir,
                size=size
            ))
        return entries
    
    # ============ File Info ============
    
    def exists(self, path: str) -> bool:
        """Check if path exists using PROPFIND instead of HEAD"""
        try:
            self._client.info(path)
            return True
        except Exception:
            return False
    
    def isdir(self, path: str) -> bool:
        """Check if path is directory"""
        try:
            info = self._client.info(path)
            # Some WebDAV servers don't return 'isdir', check by:
            # 1. Explicit 'isdir' field
            # 2. Directory has no content_type and size is None
            if 'isdir' in info:
                return info.get('isdir', False)
            # Heuristic: directories have no content_type and size is None
            return info.get('content_type') is None and info.get('size') is None
        except Exception:
            return False
    
    def isfile(self, path: str) -> bool:
        """Check if path is file"""
        try:
            info = self._client.info(path)
            # Some WebDAV servers don't return 'isdir', check by:
            # 1. Explicit 'isdir' field
            # 2. File has content_type or size is not None
            if 'isdir' in info:
                return not info.get('isdir', True)
            # Heuristic: files have content_type or size is not None
            return info.get('content_type') is not None or info.get('size') is not None
        except Exception:
            return False
    
    def stat(self, path: str) -> FileStat:
        """Get file/directory info"""
        info = self._client.info(path)
        
        # Parse size (may be string, None, or int)
        size_val = info.get('size')
        if size_val is None:
            size = 0
        elif isinstance(size_val, str):
            size = int(size_val) if size_val.isdigit() else 0
        else:
            size = int(size_val)
        
        # Parse modified time (may be RFC 2822 string, timestamp, or None)
        mtime_val = info.get('modified')
        if mtime_val is None:
            mtime = 0.0
        elif isinstance(mtime_val, str):
            # Parse RFC 2822 date format: "Fri, 02 Jan 2026 15:26:26 GMT"
            try:
                from email.utils import parsedate_to_datetime
                mtime = parsedate_to_datetime(mtime_val).timestamp()
            except Exception:
                mtime = 0.0
        else:
            mtime = float(mtime_val)
        
        # Check isdir
        is_dir = info.get('isdir', False)
        if not isinstance(is_dir, bool):
            # Heuristic: directories have no content_type and size is None
            is_dir = info.get('content_type') is None and info.get('size') is None
        
        return FileStat(
            size=size,
            mtime=mtime,
            is_dir=is_dir,
            name=path.rstrip('/').split('/')[-1],
            path=path
        )
    
    def getsize(self, path: str) -> int:
        """Get file size"""
        return self.stat(path).size
    
    # ============ File Management ============
    
    def remove(self, path: str):
        """Remove file"""
        self._client.clean(path)
    
    unlink = remove
    
    def rename(self, src: str, dst: str):
        """Rename/move file"""
        # Use direct MOVE request to avoid webdavclient3's internal check() calls
        from webdav3.urn import Urn
        urn_from = Urn(src)
        urn_to = Urn(dst)
        header_destination = f"Destination: {self._client.get_url(urn_to.quote())}"
        header_overwrite = "Overwrite: T"  # Allow overwrite to avoid 412 errors
        self._client.execute_request(action='move', path=urn_from.quote(), 
                                     headers_ext=[header_destination, header_overwrite])
    
    def copy(self, src: str, dst: str):
        """Copy file"""
        # Use direct COPY request to avoid webdavclient3's internal check() calls
        from webdav3.urn import Urn
        urn_from = Urn(src)
        urn_to = Urn(dst)
        header_destination = f"Destination: {self._client.get_url(urn_to.quote())}"
        header_overwrite = "Overwrite: T"  # Allow overwrite to avoid 412 errors
        self._client.execute_request(action='copy', path=urn_from.quote(),
                                     headers_ext=[header_destination, header_overwrite])
    
    # ============ Lock Operations ============
    
    def lock(self, path: str, timeout: int = 3600) -> Optional[str]:
        """
        Acquire lock on file
        
        Args:
            path: File path to lock
            timeout: Lock timeout in seconds (default 1 hour)
            
        Returns:
            Lock token if successful, None if failed
        """
        import requests
        from webdav3.urn import Urn
        
        urn = Urn(path)
        url = self._client.get_url(urn.quote())
        
        # WebDAV LOCK request body
        lock_body = '''<?xml version="1.0" encoding="utf-8"?>
<D:lockinfo xmlns:D="DAV:">
  <D:lockscope><D:exclusive/></D:lockscope>
  <D:locktype><D:write/></D:locktype>
</D:lockinfo>'''
        
        headers = {
            'Content-Type': 'application/xml',
            'Timeout': f'Second-{timeout}',
        }
        
        # Get auth from webdavclient3
        auth = None
        if hasattr(self._client, 'webdav') and self._client.webdav.login:
            auth = (self._client.webdav.login, self._client.webdav.password)
        
        try:
            response = requests.request('LOCK', url, data=lock_body, headers=headers, auth=auth)
            if response.status_code in (200, 201):
                # Extract lock token from response
                import re
                match = re.search(r'<D:locktoken>.*?<D:href>([^<]+)</D:href>', response.text, re.DOTALL)
                if match:
                    return match.group(1)
                # Try alternative format
                match = re.search(r'opaquelocktoken:[^<]+', response.text)
                if match:
                    return match.group(0)
                return "lock-token-unknown"
            else:
                raise WebDAVLockError(f"LOCK failed with status {response.status_code}: {response.text}")
        except requests.RequestException as e:
            raise WebDAVLockError(f"Failed to acquire lock: {e}")
    
    def unlock(self, path: str, token: str):
        """
        Release lock on file
        
        Args:
            path: File path to unlock
            token: Lock token from lock()
        """
        import requests
        from webdav3.urn import Urn
        
        urn = Urn(path)
        url = self._client.get_url(urn.quote())
        
        headers = {
            'Lock-Token': f'<{token}>' if not token.startswith('<') else token,
        }
        
        # Get auth from webdavclient3
        auth = None
        if hasattr(self._client, 'webdav') and self._client.webdav.login:
            auth = (self._client.webdav.login, self._client.webdav.password)
        
        try:
            response = requests.request('UNLOCK', url, headers=headers, auth=auth)
            if response.status_code not in (200, 204):
                raise WebDAVLockError(f"UNLOCK failed with status {response.status_code}")
        except requests.RequestException as e:
            raise WebDAVLockError(f"Failed to release lock: {e}")


# ============================================================================
# WebDAV File Object (High-level)
# ============================================================================

class WebDAVFile:
    """
    File-like object for WebDAV
    
    Provides Python file API over WebDAV:
    - Read/write operations
    - Context manager support
    - Text/binary modes
    """
    
    def __init__(self, client: WebDAVClient, path: str, mode: str = 'r',
                 encoding: Optional[str] = None):
        """
        Open WebDAV file
        
        Args:
            client: WebDAV client
            path: Remote file path
            mode: Open mode ('r', 'w', 'rb', 'wb', 'a', 'ab')
            encoding: Text encoding (default: 'utf-8', ignored in binary mode)
        """
        self._client = client
        self._path = path
        self._mode = mode
        self._binary = 'b' in mode
        self._encoding = None if self._binary else (encoding or 'utf-8')
        self._closed = False
        
        # Buffer for write operations
        self._buffer = io.BytesIO()
        self._dirty = False
        self._position = 0
        
        # Load existing content for read/append modes
        if 'r' in mode or 'a' in mode or '+' in mode:
            if client.exists(path):
                data = client.download_bytes(path)
                self._buffer = io.BytesIO(data)
                if 'a' in mode:
                    self._buffer.seek(0, 2)  # Seek to end for append
                    self._position = len(data)
            elif 'r' in mode and 'w' not in mode and '+' not in mode:
                raise FileNotFoundError(f"File not found: {path}")
    
    @property
    def closed(self) -> bool:
        return self._closed
    
    @property
    def mode(self) -> str:
        return self._mode
    
    @property
    def name(self) -> str:
        return self._path
    
    def read(self, size: int = -1) -> Union[bytes, str]:
        """Read data"""
        if self._closed:
            raise ValueError("I/O operation on closed file")
        
        if size == -1:
            data = self._buffer.read()
        else:
            data = self._buffer.read(size)
        
        if self._binary:
            return data
        return data.decode(self._encoding)
    
    def readline(self) -> Union[bytes, str]:
        """Read a line"""
        if self._closed:
            raise ValueError("I/O operation on closed file")
        
        data = self._buffer.readline()
        if self._binary:
            return data
        return data.decode(self._encoding)
    
    def readlines(self) -> List[Union[bytes, str]]:
        """Read all lines"""
        lines = []
        while True:
            line = self.readline()
            if not line:
                break
            lines.append(line)
        return lines
    
    def write(self, data: Union[bytes, str]) -> int:
        """Write data"""
        if self._closed:
            raise ValueError("I/O operation on closed file")
        
        if isinstance(data, str):
            data = data.encode(self._encoding or 'utf-8')
        
        written = self._buffer.write(data)
        self._dirty = True
        return written
    
    def writelines(self, lines):
        """Write multiple lines"""
        for line in lines:
            self.write(line)
    
    def seek(self, offset: int, whence: int = 0) -> int:
        """Seek to position"""
        return self._buffer.seek(offset, whence)
    
    def tell(self) -> int:
        """Get current position"""
        return self._buffer.tell()
    
    def flush(self):
        """Flush buffer to remote"""
        if self._dirty and not self._closed:
            pos = self._buffer.tell()
            self._buffer.seek(0)
            self._client.upload_bytes(self._path, self._buffer.getvalue())
            self._buffer.seek(pos)
            self._dirty = False
    
    def truncate(self, size: Optional[int] = None) -> int:
        """Truncate file to specified size"""
        if self._closed:
            raise ValueError("I/O operation on closed file")
        
        if size is None:
            size = self._buffer.tell()
        
        # Truncate the buffer
        self._buffer.seek(0)
        data = self._buffer.read(size)
        self._buffer = io.BytesIO(data)
        self._buffer.seek(min(size, len(data)))
        self._dirty = True
        return len(data)
    
    def close(self):
        """Close file and upload if modified"""
        if not self._closed:
            if self._dirty and ('w' in self._mode or 'a' in self._mode or '+' in self._mode):
                self.flush()
            self._closed = True
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
    
    def __iter__(self):
        return self
    
    def __next__(self):
        line = self.readline()
        if not line:
            raise StopIteration
        return line


# ============================================================================
# WebDAV FileSystem (High-level API with User Isolation)
# ============================================================================

class WebDAVFileSystem:
    """
    User-isolated WebDAV FileSystem
    
    All paths are prefixed with: /{pid}/{fs_name}/{oid}/{uid}/
    """
    
    def __init__(self, hostname: str, username: Optional[str] = None,
                 password: Optional[str] = None, auto_mkdir: bool = True,
                 timeout: int = 30):
        """
        Initialize WebDAV FileSystem
        
        Args:
            hostname: WebDAV server URL (e.g., "http://10.0.0.1:5000")
            username: Username for authentication
            password: Password for authentication
            auto_mkdir: Auto create user directory
            timeout: Connection timeout in seconds
        """
        self._client = WebDAVClient(hostname, username, password, timeout)
        
        if auto_mkdir:
            self._ensure_user_dir()
    
    def _get_base_path(self) -> str:
        """Get user base path from config
        
        Path format: /{oid}/{uid}
        """
        from ..config import env
        return f"/{env.storage.oid}/{env.storage.uid}"
    
    def _create_path(self, path: str) -> str:
        """Create full path with user prefix"""
        path = path.strip('/')
        base = self._get_base_path()
        return f"{base}/{path}" if path else base
    
    def _is_path_allowed(self, full_path: str) -> bool:
        """Check if path is within user directory"""
        base = os.path.normpath(self._get_base_path())
        normalized = os.path.normpath(full_path)
        return normalized == base or normalized.startswith(base + '/')
    
    def _safe_path(self, path: str) -> str:
        """Create and validate path"""
        full_path = self._create_path(path)
        if not self._is_path_allowed(full_path):
            raise PermissionError(f"Path not allowed: {path}")
        return full_path
    
    def _ensure_user_dir(self):
        """Ensure user directory exists"""
        try:
            self._client.mkdir(self._get_base_path(), parents=True)
        except Exception:
            pass
    
    @property
    def base_path(self) -> str:
        """User base path"""
        return self._get_base_path()
    
    # ============ File Operations ============
    
    def open(self, path: str, mode: str = 'r',
             encoding: Optional[str] = None) -> WebDAVFile:
        """Open file"""
        full_path = self._safe_path(path)
        
        # Auto create parent directory for write modes
        if any(c in mode for c in 'wax'):
            parent = '/'.join(full_path.split('/')[:-1])
            if parent:
                try:
                    self._client.mkdir(parent, parents=True)
                except Exception:
                    pass
        
        return WebDAVFile(self._client, full_path, mode, encoding)
    
    @contextmanager
    def locked_open(self, path: str, mode: str = 'r', timeout: int = 3600):
        """Open file with lock"""
        full_path = self._safe_path(path)
        token = None
        
        try:
            token = self._client.lock(full_path, timeout)
            f = WebDAVFile(self._client, full_path, mode)
            yield f
            f.close()
        finally:
            if token:
                try:
                    self._client.unlock(full_path, token)
                except Exception:
                    pass
    
    # ============ Directory Operations ============
    
    def mkdir(self, path: str, parents: bool = False, exist_ok: bool = False):
        """Create directory"""
        full_path = self._safe_path(path)
        try:
            self._client.mkdir(full_path, parents=parents)
        except Exception as e:
            if not exist_ok:
                raise
    
    def rmdir(self, path: str):
        """Remove directory"""
        self._client.rmdir(self._safe_path(path))
    
    def listdir(self, path: str = "") -> List[str]:
        """List directory contents"""
        return self._client.listdir(self._safe_path(path))
    
    def scandir(self, path: str = "") -> List[DirEntry]:
        """List directory with details"""
        return self._client.scandir(self._safe_path(path))
    
    def walk(self, path: str = "") -> Generator:
        """Recursively traverse directory"""
        full_path = self._safe_path(path)
        base_len = len(self._get_base_path())
        
        def _walk(current_path):
            entries = self._client.scandir(current_path)
            dirs = []
            files = []
            
            for entry in entries:
                if entry.is_dir:
                    dirs.append(entry.name)
                else:
                    files.append(entry.name)
            
            rel_path = current_path[base_len:].lstrip('/')
            yield (rel_path, dirs, files)
            
            for d in dirs:
                yield from _walk(current_path.rstrip('/') + '/' + d)
        
        yield from _walk(full_path)
    
    # ============ File Info ============
    
    def exists(self, path: str) -> bool:
        return self._client.exists(self._safe_path(path))
    
    def isfile(self, path: str) -> bool:
        return self._client.isfile(self._safe_path(path))
    
    def isdir(self, path: str) -> bool:
        return self._client.isdir(self._safe_path(path))
    
    def stat(self, path: str) -> FileStat:
        return self._client.stat(self._safe_path(path))
    
    def getsize(self, path: str) -> int:
        return self._client.getsize(self._safe_path(path))
    
    # ============ File Management ============
    
    def remove(self, path: str):
        """Remove file"""
        self._client.remove(self._safe_path(path))
    
    unlink = remove
    
    def rename(self, src: str, dst: str):
        """Rename/move file"""
        self._client.rename(self._safe_path(src), self._safe_path(dst))
    
    def copy(self, src: str, dst: str):
        """Copy file"""
        self._client.copy(self._safe_path(src), self._safe_path(dst))
    
    # ============ Context Manager ============
    
    def close(self):
        """Close client (no-op for WebDAV, kept for API compatibility)"""
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

