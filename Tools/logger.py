import os
import pathlib
import logging
import asyncio
import sys

from aiologger import Logger
from aiologger.handlers.streams import AsyncStreamHandler
from aiologger.handlers.files import AsyncFileHandler
from aiologger.formatters.base import Formatter

from Tools.Misc import FuncUtils
from Tools.files import FileStreams, FileUtils


# This is my uselessly complicated logging system
# It creates a loggers object by which you can create loggers and access it as a attribute of the loggers object
# The main part of this is to have all your log files in a folder and then you can use the organize function to organize them in old logs sorted by date

class Loggers:

    def __init__(self, log_path:str) -> None:
        if((er := FuncUtils.checkargs(["log_path"])) != None):
            raise Exception(er)
        self.all_loggers = dict()
        self.log_path = log_path
        
    def CreateLogger(self, name: str, logginglevel: str, filename: str, Streamhandler: bool = False, Filehandler:bool = True, format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'):
        if((er := FuncUtils.checkargs(["logginglevel", "name", "filename", "Streamhandler", "Filehandler"])) != None):
            raise Exception(er)
        
        if([key for key,val in self.all_loggers.items() if key == name]):
            raise Exception("cannot have 2 loggers with same name")
        if([val for key,val in self.all_loggers.items() if val[1] == filename]):
            raise Exception("cannot have 2 loggers with same name")
        formatter = Formatter(format)
        logger = Logger(name=name,level=logginglevel)


        if(Streamhandler):
            streamhandler = AsyncStreamHandler(stream=sys.stdout)
            streamhandler.level = logginglevel
            streamhandler.formatter = formatter
            logger.add_handler(streamhandler)

        if(Filehandler):
            filehandler = AsyncFileHandler(os.path.join(self.log_path, filename))
            filehandler.level = logginglevel
            filehandler.formatter = formatter
            logger.add_handler(filehandler)

        setattr(self, name, logger)
        self.all_loggers[name] = [logger, filename]
        
        return logger

    async def organize(self) -> None: #did not make this async because it should be used at end of program not between lol
        Files = FileStreams()
        for filename in os.listdir(self.log_path):
            file = os.path.join(self.log_path, filename)
            if(str(file).endswith(".log")):
                filewrapper = Files.AddStream(filename,  file)
                async with await filewrapper.openwithmode("r") as logfile: 
                    writefile = None
                    lastdate = None
                    for line in await logfile.readlines():
                        line = str(line).strip()
                        date = line.split()[0]
                        if(lastdate != date):
                            writepath = os.path.join(self.log_path, "old", date, filename)
                            FileUtils.makefile(writepath)
                            writefilewrapper = None
                            if(ez := [val for key,val in Files.all_streams.items() if val.filepath == writepath]):
                                writefilewrapper = ez[0]
                            else:
                                writefilewrapper = Files.AddStream(date + filename, writepath)  #this is evry inefficient - too lazy to write better code
                                await writefilewrapper.openwithmode("a+", contextmanager=False)
                            writefile = writefilewrapper.stream
                        await writefile.write(line + "\n")
                        lastdate = date 
        for filename, stream in Files.all_streams.items():
            await stream.closestream() 

#--------------------------------------
# Usage example
#--------------------------------------
#
# async def main():
#     loggers = Loggers('/'.join(str(pathlib.Path(__file__).parent.absolute()).split("/")[0:-1]) + "/data/logs")
#     loggers.CreateLogger("logger1", "NOTSET", "test.log", True, True)
#     await loggers.logger1.debug("Hello world") 
#     loggers.organize()
#
# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())
# loop.close()
