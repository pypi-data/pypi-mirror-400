from ...exceptions import *
from ...utils import _validate_path, _validate_permission, _query

from httpx import Response
import aiofiles, asyncio, os, time, logging
from typing import Optional, Callable, AsyncIterator, Literal
from abc import ABC, abstractmethod
from getpass import getuser


class AsyncWebHDFSInterface(ABC):
    
    def __init__(
        self,
        protocol: Literal['http','https'] = 'http',
        host: str = 'localhost',
        port: int = 9870,
        user: str = getuser(),
    ):
        self._user = user
        self._base = f'{protocol}://{host}:{port}/webhdfs/v1'
        self._logging = logging
    
    _validate_path = _validate_path
    _validate_permission = _validate_permission
    _query = _query
    
    async def _file_streamer(
        self,
        path: str,
        chunk_size: int = 1024 * 1024,  # 1 MB default
        progress_cb: Optional[Callable[[int, int], None]] = None,
        rate_limit_bps: Optional[int] = None
    ) -> AsyncIterator[bytes]:
        """
        Asynchronous generator for streaming file content in chunks with progress reporting and rate limiting.
        
        Args:
            path: Local file path.
            chunk_size: Number of bytes to read per iteration.
            progress_cb: Optional async callback called as progress_cb(bytes_sent, total_bytes).
            rate_limit_bps: Optional maximum bytes per second to stream (bandwidth control).
        
        Yields:
            bytes: Chunks of file content.
        """
        total_size = os.path.getsize(path)
        sent = 0
        start_time = time.monotonic()
        
        async with aiofiles.open(path, 'rb') as f:
            while True:
                chunk = await f.read(chunk_size)
                if not chunk:
                    break
                
                sent += len(chunk)
                
                if rate_limit_bps:
                    elapsed = time.monotonic() - start_time
                    expected_elapsed = sent / rate_limit_bps
                    if expected_elapsed > elapsed:
                        await asyncio.sleep(expected_elapsed - elapsed)
                
                if progress_cb:
                    maybe_coro = progress_cb(sent, total_size)
                    if asyncio.iscoroutine(maybe_coro):
                        await maybe_coro
                
                yield chunk
    
    @abstractmethod
    async def append(
        self,
        path: str,
        file: str = None,
        buffersize: int = None, 
        noredirect: bool = False
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    async def create(
        self,
        path: str,
        file: str = None,
        overwrite: bool = False,
        blocksize: int = None,
        replication: int = None,
        permission: str = '644',
        buffersize: int = None, 
        noredirect: bool = False,
        createparent: bool = False
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    async def delete(
        self,
        path: str,
        recursive: bool = False
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    async def getcontentsummary(
        self,
        path: str
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    async def getfilechecksum(
        self,
        path: str,
        noredirect: bool = False
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    async def getfilestatus(
        self,
        path: str
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    async def gethomedirectory(
        self
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    async def liststatus(
        self,
        path: str
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    async def mkdirs(
        self,
        path: str,
        permission: str = '755'
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    async def open(
        self,
        path: str, 
        offset: int = 0, 
        length: int = None, 
        buffersize: int = None,
        noredirect: bool = False
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    async def rename(
        self,
        path: str,
        destination: str
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    async def setowner(
        self,
        path: str,
        owner: Optional[str] = None,
        group: Optional[str] = None
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    async def setpermission(
        self,
        path: str,
        permission: str
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    async def settimes(
        self,
        path: str,
        modificationtime: int = -1,
        accesstime: int = -1
    ) -> Response:
        raise NotImplementedError
            
