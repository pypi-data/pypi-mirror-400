from abc import ABC, abstractmethod
from typing import Optional, Literal
from httpx import Response
from getpass import getuser


class WebHDFSInterface(ABC):
    
    def __init__(
        self,
        protocol: Literal['http','https'] = 'http',
        host: str = 'localhost',
        port: int = 9870,
        user: str = getuser(),
    ):
        self._protocol = protocol
        self._host = host
        self._port = port
        self._user = user
    
    @abstractmethod
    def append(
        self,
        path: str,
        file: str = None,
        buffersize: int = None, 
        noredirect: bool = False
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    def create(
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
    def delete(
        self,
        path: str,
        recursive: bool = False
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    def getcontentsummary(
        self,
        path: str
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    def getfilechecksum(
        self,
        path: str,
        noredirect: bool = False
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    def getfilestatus(
        self,
        path: str
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    def gethomedirectory(self) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    def liststatus(
        self,
        path: str
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    def mkdirs(
        self,
        path: str,
        permission: str = '755'
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    def open(
        self,
        path: str, 
        offset: int = 0, 
        length: int = None, 
        buffersize: int = None,
        noredirect: bool = False
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    def rename(
        self,
        path: str,
        destination: str
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    def setowner(
        self,
        path: str,
        owner: Optional[str] = None,
        group: Optional[str] = None
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    def setpermission(
        self,
        path: str,
        permission: str
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    def settimes(
        self,
        path: str,
        modificationtime: int = -1,
        accesstime: int = -1
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    async def aappend(
        self,
        path: str,
        file: str = None,
        buffersize: int = None, 
        noredirect: bool = False
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    async def acreate(
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
    async def adelete(
        self,
        path: str,
        recursive: bool = False
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    async def agetcontentsummary(
        self,
        path: str
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    async def agetfilechecksum(
        self,
        path: str,
        noredirect: bool = False
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    async def agetfilestatus(
        self,
        path: str
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    async def agethomedirectory(
        self
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    async def aliststatus(
        self,
        path: str
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    async def amkdirs(
        self,
        path: str,
        permission: str = '755'
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    async def aopen(
        self,
        path: str, 
        offset: int = 0, 
        length: int = None, 
        buffersize: int = None,
        noredirect: bool = False
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    async def arename(
        self,
        path: str,
        destination: str
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    async def asetowner(
        self,
        path: str,
        owner: Optional[str] = None,
        group: Optional[str] = None
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    async def asetpermission(
        self,
        path: str,
        permission: str
    ) -> Response:
        raise NotImplementedError
    
    @abstractmethod
    async def asettimes(
        self,
        path: str,
        modificationtime: int = -1,
        accesstime: int = -1
    ) -> Response:
        raise NotImplementedError
