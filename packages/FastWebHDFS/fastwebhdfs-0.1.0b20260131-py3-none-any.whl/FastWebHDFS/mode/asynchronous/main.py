from ...exceptions import *
from .base import AsyncWebHDFSInterface

from httpx import AsyncClient, Response, RequestError
from typing import Optional

            
class AsyncWebHDFS(AsyncWebHDFSInterface):
    
    async def append(
        self,
        path: str,
        file: str = None,
        buffersize: int = None, 
        noredirect: bool = False
    ) -> Response:
        """Append to a File
        
        ```{bash}
        curl -i -X POST "http://<HOST>:<PORT>/webhdfs/v1/<PATH>?op=APPEND[&buffersize=<INT>][&noredirect=<true|false>]"
        curl -i -X POST -T <LOCAL_FILE> "http://<DATANODE>:<PORT>/webhdfs/v1/<PATH>?op=APPEND..."
        ```
        """
        path: str = self._validate_path(path)
        content: bytes = self._file_streamer(file) if file else bytes()
        query: str = self._query(
            {
                'op': 'APPEND',
                'user.name': self._user,
                'buffersize': buffersize,
                'noredirect': noredirect,
            }
        )
        url1: str = f"{self._base}{path}?{query}"
        try:
            self._logging.info(url1)
            async with AsyncClient() as client:
                step1: Response = await client.post(url1, timeout=10.0)
        except RequestError as e:
            self._logging.error(e)
            raise
        
        match step1.status_code, noredirect:
            case 307, False:
                url2 = step1.headers['Location']
            case 200, True:
                url2 = step1.json()['Location']
            case _:
                raise WebHDFSException(step1)
        
        try:
            self._logging.info(url2)
            async with AsyncClient() as client:
                step2: Response = await client.post(url2, content=content, timeout=10.0)
        except RequestError as e:
            self._logging.error(e)
            raise
        
        if step2.status_code == 200:
            return step2
        else:
            match step2.status_code, step2.json()['RemoteException']['exception']:
                case _:
                    raise WebHDFSException(step2)
    
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
        """
        """
        path: str = self._validate_path(path)
        content: bytes = self._file_streamer(file) if file else bytes()
        query = self._query(
            {
                'op': 'CREATE',
                'user.name': self._user,
                'overwrite': overwrite,
                'blocksize': blocksize,
                'replication': replication,
                'permission': self._validate_permission(permission),
                'buffersize': buffersize,
                'noredirect': noredirect,
                'createparent': createparent
            }
        )
        url1 = f"{self._base}{path}?{query}"
        try:
            self._logging.info(url1)
            async with AsyncClient() as client:
                step1: Response = await client.put(url1, timeout=10.0)
        except RequestError as e:
            self._logging.error(e)
            raise
        
        match step1.status_code, noredirect:
            case 307, False:
                url2 = step1.headers['Location']
            case 200, True:
                url2 = step1.json()['Location']
            case _:
                raise WebHDFSException(step1)
        
        try:
            self._logging.info(url2)
            async with AsyncClient() as client:
                step2: Response = await client.put(url2, content=content, timeout=10.0)
        except RequestError as e:
            self._logging.error(e)
            raise
        
        if step2.status_code == 201:
            return step2
        else:
            match step2.status_code, step2.json()['RemoteException']['exception']:
                case 403, 'FileAlreadyExistsException':
                    raise FileAlreadyExistsException(step2)
                case 404, 'FileNotFoundException':
                    raise FileNotFoundException(step2)
                case _:
                    raise WebHDFSException(step2)
    
    async def delete(
        self,
        path: str,
        recursive: bool = False
    ) -> Response:
        """Delete a File/Directory
        
        ```{bash}
        # https://hadoop.apache.org/docs/r3.3.6/hadoop-project-dist/hadoop-hdfs/WebHDFS.html#Delete_a_File.2FDirectory
        curl -i -X DELETE "http://<host>:<port>/webhdfs/v1/<path>?op=DELETE[&recursive=<true |false>]"
        ```
        """
        path = self._validate_path(path)
        query = self._query(
            {
                'op': 'DELETE',
                'user.name': self._user,
                'recursive': recursive
            }
        )
        url = f"{self._base}{path}?{query}"
        try:
            self._logging.info(url)
            async with AsyncClient() as client:
                response: Response = await client.delete(url, timeout=10.0)
        except RequestError as e:
            self._logging.error(e)
            raise
        
        if response.status_code == 200:
            return response
        else:
            match response.status_code, response.json()['RemoteException']['exception']:
                case 404, 'FileNotFoundException':
                    raise FileNotFoundException(response)
                case _:
                    raise WebHDFSException(response)
    
    async def getcontentsummary(
        self,
        path: str
    ) -> Response:
        """Get Content Summary of a Directory
        
        ```{bash}
        curl -i "http://<HOST>:<PORT>/webhdfs/v1/<PATH>?op=GETCONTENTSUMMARY"
        ```
        """
        path: str = self._validate_path(path)
        query: str = self._query(
            {
                'op': 'GETCONTENTSUMMARY',
                'user.name': self._user
            }
        )
        url = f"{self._base}{path}?{query}"
        try:
            self._logging.info(url)
            async with AsyncClient() as client:
                response: Response = await client.get(url, timeout=10.0)
        except RequestError as e:
            self._logging.error(e)
            raise
        
        if response.status_code == 200:
            return response
        else:
            match response.status_code, response.json()['RemoteException']['exception']:
                case _:
                    raise WebHDFSException(response)
    
    async def getfilechecksum(
        self,
        path: str,
        noredirect: bool = False
    ) -> Response:
        """
        curl -i  "http://<HOST>:<PORT>/webhdfs/v1/<PATH>?op=GETFILECHECKSUM"
        """
        path: str = self._validate_path(path)
        query: str = self._query(
            {
                'op': 'GETFILECHECKSUM',
                'user.name': self._user,
                'noredirect': noredirect
            }
        )
        url1 = f"{self._base}{path}?{query}"
        try:
            self._logging.info(url1)
            async with AsyncClient() as client:
                step1: Response = await client.get(url1, timeout=10.0)
        except RequestError as e:
            self._logging.error(e)
            raise
        
        match step1.status_code, noredirect:
            case 307, False:
                url2 = step1.headers['Location']
            case 200, True:
                url2 = step1.json()['Location']
            case _:
                raise WebHDFSException(step1)
        
        try:
            self._logging.info(url2)
            async with AsyncClient() as client:
                step2: Response = await client.get(url2, timeout=10.0)
        except RequestError as e:
            self._logging.error(e)
            raise
        
        if step2.status_code == 200:
            return step2
        else:
            match step2.status_code, step2.json()['RemoteException']['exception']:
                case _:
                    raise WebHDFSException(step2)
    
    async def getfilestatus(
        self,
        path: str
    ) -> Response:
        """
        https://hadoop.apache.org/docs/r3.3.6/hadoop-project-dist/hadoop-hdfs/WebHDFS.html#List_a_Directory
        https://hadoop.apache.org/docs/r3.3.6/hadoop-project-dist/hadoop-hdfs/WebHDFS.html#List_a_File
        curl -i  "http://<HOST>:<PORT>/webhdfs/v1/<PATH>?op=LISTSTATUS"
        # curl -i  "http://<HOST>:<PORT>/webhdfs/v1/<PATH>?op=LISTSTATUS_BATCH&startAfter=bazfile"
        """
        path: str = self._validate_path(path)
        query: str = self._query(
            {
                'user.name': self._user,
                'op': 'GETFILESTATUS'
            }
        )
        url: str = f"{self._base}{path}?{query}"
        try:
            self._logging.info(url)
            async with AsyncClient() as client:
                response: Response = await client.get(url, timeout=10.0)
        except RequestError as e:
            self._logging.error(e)
            raise
        
        if response.status_code == 200:
            return response
        else:
            match response.status_code, response.json()['RemoteException']['exception']:
                case _:
                    raise WebHDFSException(response)
    
    async def gethomedirectory(self) -> Response:
        """
        curl -i  "http://<HOST>:<PORT>/webhdfs/v1/?op=GETHOMEDIRECTORY"
        """
        path: str = '/'
        query: str = self._query(
            {
                'user.name': self._user,
                'op': 'GETHOMEDIRECTORY'
            }
        )
        url: str = f"{self._base}{path}?{query}"
        try:
            self._logging.info(url)
            async with AsyncClient() as client:
                response: Response = await client.get(url, timeout=10.0)
        except RequestError as e:
            self._logging.error(e)
            raise
        
        if response.status_code == 200:
            return response
        else:
            match response.status_code, response.json()['RemoteException']['exception']:
                case _:
                    raise WebHDFSException(response)
    
    async def liststatus(
        self,
        path: str
    ) -> Response:
        """
        https://hadoop.apache.org/docs/r3.3.6/hadoop-project-dist/hadoop-hdfs/WebHDFS.html#List_a_Directory
        https://hadoop.apache.org/docs/r3.3.6/hadoop-project-dist/hadoop-hdfs/WebHDFS.html#List_a_File
        curl -i  "http://<HOST>:<PORT>/webhdfs/v1/<PATH>?op=LISTSTATUS"
        # curl -i  "http://<HOST>:<PORT>/webhdfs/v1/<PATH>?op=LISTSTATUS_BATCH&startAfter=bazfile"
        """
        path: str = self._validate_path(path)
        query: str = self._query(
            {
                'user.name': self._user,
                'op': 'LISTSTATUS'
            }
        )
        url: str = f"{self._base}{path}?{query}"
        try:
            self._logging.info(url)
            async with AsyncClient() as client:
                response: Response = await client.get(url, timeout=10.0)
        except RequestError as e:
            self._logging.error(e)
            raise
        
        if response.status_code == 200:
            return response
        else:
            match response.status_code, response.json()['RemoteException']['exception']:
                case 404, 'FileNotFoundException':
                    raise FileNotFoundException(response)
                case _:
                    raise WebHDFSException(response)
    
    async def mkdirs(
        self,
        path: str,
        permission: str = '755'
    ) -> Response:
        """
        Create directories in HDFS using WebHDFS MKDIRS.
        
        ```{bash}
        # https://hadoop.apache.org/docs/r3.3.6/hadoop-project-dist/hadoop-hdfs/WebHDFS.html#Make_a_Directory
        curl -i -X PUT "http://<HOST>:<PORT>/webhdfs/v1/<PATH>?op=MKDIRS[&permission=<OCTAL>]
        ```
        
        Linux-like behavior:
        - permission must be raw octal string (e.g., "755", "1777")
        """
        path: str = self._validate_path(path)
        query: str = self._query(
            {
                "user.name": self._user,
                "op": "MKDIRS",
                "permission": self._validate_permission(permission),
            }
        )
        url: str = f"{self._base}{path}?{query}"
        try:
            self._logging.info(url)
            async with AsyncClient() as client:
                response: Response = await client.put(url, timeout=10.0)
        except RequestError as e:
            self._logging.error(e)
            raise
        
        if response.status_code == 200:
            return response
        else:
            match response.status_code, response.json()['RemoteException']['exception']:
                case 403, 'FileAlreadyExistsException':
                    raise FileAlreadyExistsException(response)
                case 403, 'ParentNotDirectoryException':
                    raise ParentNotDirectoryException(response)
                case _:
                    raise WebHDFSException(response)
    
    async def open(
        self,
        path: str, 
        offset: int = 0, 
        length: int = None, 
        buffersize: int = None,
        noredirect: bool = False
    ) -> Response:
        path: str = self._validate_path(path)
        query: str = self._query(
            {
                'op': 'OPEN',
                'user.name': self._user,
                'offset': offset, 
                'length': length, 
                'buffersize': buffersize,
                'noredirect': noredirect
            }
        )
        url1: str = f"{self._base}{path}?{query}"
        try:
            self._logging.info(url1)
            async with AsyncClient() as client:
                step1: Response = await client.get(url1, timeout=10.0)
        except RequestError as e:
            self._logging.error(e)
            raise
        
        match step1.status_code, noredirect:
            case 307, False:
                url2: str = step1.headers['Location']
            case 200, True:
                url2: str = step1.json()['Location']
            case _:
                raise WebHDFSException(step1)
        
        try:
            self._logging.info(url2)
            async with AsyncClient() as client:
                step2: Response = await client.get(url2, timeout=10.0)
        except RequestError as e:
            self._logging.error(e)
            raise
        
        if step2.status_code == 200:
            return step2
        else:
            match step2.status_code, step2.json()['RemoteException']['exception']:
                case 403, 'FileAlreadyExistsException':
                    raise FileAlreadyExistsException(step2)
                case _:
                    raise WebHDFSException(step2)
    
    async def rename(
        self,
        path: str,
        destination: str
    ) -> Response:
        """
        Rename a file/directory in HDFS using WebHDFS DELETE.
        
        ```{bash}
        curl -i -X PUT "<HOST>:<PORT>/webhdfs/v1/<PATH>?op=RENAME&destination=<PATH>"
        ```
        """
        path: str = self._validate_path(path)
        query: str = self._query(
            {
                'op': 'RENAME',
                'user.name': self._user,
                'destination': destination
            }
        )
        url: str = f"{self._base}{path}?{query}"
        try:
            self._logging.info(url)
            async with AsyncClient() as client:
                response: Response = await client.put(url, timeout=10.0)
        except RequestError as e:
            self._logging.error(e)
            raise
        
        if response.status_code == 200:
            return response
        else:
            match response.status_code, response.json()['RemoteException']['exception']:
                case _:
                    raise WebHDFSException(response)
    
    async def setowner(
        self,
        path: str,
        owner: Optional[str] = None,
        group: Optional[str] = None
    ) -> Response:
        """Set Owner
        
        ```{bash}
        curl -i -X PUT "http://<HOST>:<PORT>/webhdfs/v1/<PATH>?op=SETOWNER[&owner=<USER>][&group=<GROUP>]"
        ```
        """
        if owner is None and group is None:
            raise TypeError(f"Specify at least one of owner or group.")
        
        path: str = self._validate_path(path)
        query: str = self._query(
            {
                'op': 'SETOWNER',
                'user.name': self._user,
                'owner': owner,
                'group': group
            }
        )
        url: str = f"{self._base}{path}?{query}"
        try:
            self._logging.info(url)
            async with AsyncClient() as client:
                response: Response = await client.put(url, timeout=10.0)
        except RequestError as e:
            self._logging.error(e)
            raise
        
        if response.status_code == 200:
            return response
        else:
            match response.status_code, response.json()['RemoteException']['exception']:
                case _:
                    raise WebHDFSException(response)
    
    async def setpermission(
        self,
        path: str,
        permission: str
    ) -> Response:
        """Set Permission
        
        ```{bash}
        curl -i -X PUT "http://<HOST>:<PORT>/webhdfs/v1/<PATH>?op=SETPERMISSION[&permission=<OCTAL>]"
        ```
        """
        path: str = self._validate_path(path)
        query: str = self._query(
            {
                'op': 'SETPERMISSION',
                'user.name': self._user,
                'permission': self._validate_permission(permission)
            }
        )
        url: str = f"{self._base}{path}?{query}"
        try:
            self._logging.info(url)
            async with AsyncClient() as client:
                response: Response = await client.put(url, timeout=10.0)
        except RequestError as e:
            self._logging.error(e)
            raise
        
        if response.status_code == 200:
            return response
        else:
            match response.status_code, response.json()['RemoteException']['exception']:
                case _:
                    raise WebHDFSException(response)
    
    async def settimes(
        self,
        path: str,
        modificationtime: int = -1,
        accesstime: int = -1
    ) -> Response:
        """Set Permission
        
        ```{bash}
        curl -i -X PUT "http://<HOST>:<PORT>/webhdfs/v1/<PATH>?op=SETTIMES[&modificationtime=<TIME>][&accesstime=<TIME>]"
        ```
        """
        path: str = self._validate_path(path)
        query: str = self._query(
            {
                'op': 'SETTIMES',
                'user.name': self._user,
                'modificationtime': modificationtime,
                'accesstime': accesstime
            }
        )
        url: str = f"{self._base}{path}?{query}"
        try:
            self._logging.info(url)
            async with AsyncClient() as client:
                response: Response = await client.put(url, timeout=10.0)
        except RequestError as e:
            self._logging.error(e)
            raise
        
        if response.status_code == 200:
            return response
        else:
            match response.status_code, response.json()['RemoteException']['exception']:
                case _:
                    raise WebHDFSException(response)

