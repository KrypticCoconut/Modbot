import discord
from programclass import ProgramClass
import atexit
from discord.ext import commands
import asyncio
import os
import nest_asyncio
import pathlib
import importlib.util
import signal
import json
from Tools.cache import ConfigCache
import setupdatabase
import models


nest_asyncio.apply()
client = commands.Bot(command_prefix="!")


def load(programclass: ProgramClass):
    for filename in os.listdir('./cogs'):
        if filename.endswith(".py"):
            spec = importlib.util.spec_from_file_location("cog", f'cogs/{filename}')
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            module.setup(programclass)
            

        
    


async def main():

    #set up program class
    cwd = '/'.join(str(pathlib.Path(__file__).parent.absolute()).split("/"))
    programclass = ProgramClass(cwd, client)

    #set up logger
    programclass.loggers.CreateLogger("Sys", "NOTSET", "Sys.log", True, True)


    #set up json config
    streamwrapper = programclass.filestreams.AddStream("setupconf", os.path.join(cwd, "config.json"))
    async with await streamwrapper.openwithmode("r") as stream:
        programclass.config = json.loads(await stream.read())
        await programclass.loggers.Sys.debug("Loaded config: " + str(programclass.config))


    #set up main databases and sessions
    await setupdatabase.main(programclass)

    #add cogs and start bot
    load(programclass)

    await programclass.loggers.Sys.debug("Bot Started")

    await programclass.loggers.organize()
    client.run(programclass.config["token"])
    
asyncio.run(main())