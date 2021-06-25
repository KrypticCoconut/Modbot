import os
import aiofiles
import asyncio
from functools import lru_cache
from contextlib import asynccontextmanager


class FileUtils:

    @classmethod
    def makefile(cls, path:str) -> None:
        dir = "/".join(path.split("/")[0:-1])
        try:
            os.makedirs(dir)
        except FileExistsError:
            pass
        
        try:
            os.mknod(path)
        except FileExistsError:
            pass

# now this is a pretty useless class, its main purpose is to manage file connections without making new connections and maintaining optimization 
# it was also used to save before another function accesses a already open file

class FileStreams:
    def __init__(self) -> None:
        self.all_streams = dict()
    
    def AddStream(self, name: str, path: str):
        if([key for key,value in self.all_streams.items() if key == name]):
            raise Exception("cannot have streams with same name")
        stream = StreamWrapper(path, name, parent=self)
        self.all_streams[name] = stream
        setattr(self, name, stream)
        return stream
        

class StreamWrapper:
    def __init__(self,filepath: str, name:str, parent: FileStreams = None) -> None:
        self.name = name
        self.filepath = filepath
        self.status = "closed"
        self.stream = None
        self.currentmode = None
        self.parent = parent  
    

    async def closestream(self):
        if(self.stream):
            self.status = "closed"
            await self.stream.close()
            self.stream = None
            self.currentmode = None

    async def restartstream(self):
        if(self.stream):
            await self.openwithmode(self.currentmode)

    async def openwithmode(self, mode: str, contextmanager: bool = True):
        if(self.parent):
            if([x for key,x in self.parent.all_streams.items() if x.status == "open" and x.filepath == self.filepath]):
                raise Exception("cant have 2 streams open on same file")
        await self.closestream()
        self.stream = await aiofiles.open(self.filepath, mode=mode)
        
        self.currentmode = mode
        self.status = "open"

        if(contextmanager):
            return wrappercontextmanager(self)
        else:
            return self.stream

class wrappercontextmanager:
    def __init__(self, streamwrapper: StreamWrapper):
        self.filestream = streamwrapper.stream
        self.streamwrapper  = streamwrapper

    async def __aenter__(self):
        return self.filestream

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.filestream:
            await self.streamwrapper.closestream()



# async def main():
#     stream1 = FileStream("test.txt", "stream1")
#     await stream1.openwithmode("w")
    
# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())
# loop.close()
