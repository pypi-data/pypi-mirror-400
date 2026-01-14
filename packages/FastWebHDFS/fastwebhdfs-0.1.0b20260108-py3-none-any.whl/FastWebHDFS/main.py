from .base import WebHDFSInterface
from .mode import SyncWebHDFS, AsyncWebHDFS

from typing import Literal, Mapping, Union, Optional
from getpass import getuser
from httpx import Response


class FastWebHDFS(WebHDFSInterface):
    
    def __init__(
        self,
        protocol: Literal['http','https'] = 'http',
        host: str = 'localhost',
        port: int = 9870,
        user: str = getuser(),
    ):
        super().__init__(protocol, host, port, user)
        self._mode: Mapping[str,Union[SyncWebHDFS,AsyncWebHDFS]] = {
            'sync': SyncWebHDFS(self._protocol,self._host,self._port,self._user),
            'async': AsyncWebHDFS(self._protocol,self._host,self._port,self._user)
        }
    
    def append(
        self,
        path: str,
        file: str = None,
        buffersize: int = None, 
        noredirect: bool = False
    ) -> Response:
        return self._mode['sync'].append(path,file,buffersize,noredirect)
    
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
        return self._mode['sync'].create(path,file,overwrite,blocksize,replication,permission,buffersize,noredirect,createparent)
    
    def delete(
        self,
        path: str,
        recursive: bool = False
    ) -> Response:
        return self._mode['sync'].delete(path,recursive)
    
    def getcontentsummary(
        self,
        path: str
    ) -> Response:
        return self._mode['sync'].getcontentsummary(path)
    
    def getfilechecksum(
        self,
        path: str,
        noredirect: bool = False
    ) -> Response:
        return self._mode['sync'].getfilechecksum(path,noredirect)
    
    def getfilestatus(
        self,
        path: str
    ) -> Response:
        return self._mode['sync'].getfilestatus(path)
    
    def gethomedirectory(self) -> Response:
        return self._mode['sync'].gethomedirectory()
    
    def liststatus(
        self,
        path: str
    ) -> Response:
        return self._mode['sync'].liststatus(path)
    
    def mkdirs(
        self,
        path: str,
        permission: str = '755'
    ) -> Response:
        return self._mode['sync'].mkdirs(path,permission)
    
    def open(
        self,
        path: str, 
        offset: int = 0, 
        length: int = None, 
        buffersize: int = None,
        noredirect: bool = False
    ) -> Response:
        return self._mode['sync'].open(path,offset,length,buffersize,noredirect)
    
    def rename(
        self,
        path: str,
        destination: str
    ) -> Response:
        return self._mode['sync'].rename(path,destination)
    
    def setowner(
        self,
        path: str,
        owner: Optional[str] = None,
        group: Optional[str] = None
    ) -> Response:
        return self._mode['sync'].setowner(path,owner,group)
    
    def setpermission(
        self,
        path: str,
        permission: str
    ) -> Response:
        return self._mode['sync'].setpermission(path,permission)
    
    def settimes(
        self,
        path: str,
        modificationtime: int = -1,
        accesstime: int = -1
    ) -> Response:
        return self._mode['sync'].settimes(path,modificationtime,accesstime)
    
    async def aappend(
        self,
        path: str,
        file: str = None,
        buffersize: int = None, 
        noredirect: bool = False
    ) -> Response:
        return await self._mode['async'].append(path,file,buffersize,noredirect)
    
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
        return await self._mode['async'].create(path,file,overwrite,blocksize,replication,permission,buffersize,noredirect,createparent)
    
    async def adelete(
        self,
        path: str,
        recursive: bool = False
    ) -> Response:
        return await self._mode['async'].delete(path,recursive)
    
    async def agetcontentsummary(
        self,
        path: str
    ) -> Response:
        return await self._mode['async'].getcontentsummary(path)
    
    async def agetfilechecksum(
        self,
        path: str,
        noredirect: bool = False
    ) -> Response:
        return await self._mode['async'].getfilechecksum(path,noredirect)
    
    async def agetfilestatus(
        self,
        path: str
    ) -> Response:
        return await self._mode['async'].getfilestatus(path)
    
    async def agethomedirectory(
        self
    ) -> Response:
        return await self._mode['async'].gethomedirectory()
    
    async def aliststatus(
        self,
        path: str
    ) -> Response:
        return await self._mode['async'].liststatus(path)
    
    async def amkdirs(
        self,
        path: str,
        permission: str = '755'
    ) -> Response:
        return await self._mode['async'].mkdirs(path,permission)
    
    async def aopen(
        self,
        path: str, 
        offset: int = 0, 
        length: int = None, 
        buffersize: int = None,
        noredirect: bool = False
    ) -> Response:
        return await self._mode['async'].open(path,offset,length,buffersize,noredirect)
    
    async def arename(
        self,
        path: str,
        destination: str
    ) -> Response:
        return await self._mode['async'].rename(path,destination)
    
    async def asetowner(
        self,
        path: str,
        owner: Optional[str] = None,
        group: Optional[str] = None
    ) -> Response:
        return await self._mode['async'].setowner(path,owner,group)
    
    async def asetpermission(
        self,
        path: str,
        permission: str
    ) -> Response:
        return await self._mode['async'].setpermission(path,permission)
    
    async def asettimes(
        self,
        path: str,
        modificationtime: int = -1,
        accesstime: int = -1
    ) -> Response:
        return await self._mode['async'].settimes(path,modificationtime,accesstime)

