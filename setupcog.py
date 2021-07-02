import discord
from discord.ext import commands
from Tools.dpy import DiscordUtils
import discord
from programclass import ProgramClass
import asyncio
import os
import pathlib
import signal
import json
from Tools.cache import ConfigCache
import setupdatabase
import models
import importlib
from Tools.eventscheduler import EventScheduler
import importlib

@DiscordUtils.helpargs(hidden=True)
class Setup(commands.Cog):
    def __init__(self, programclass):
        self.programclass = programclass
        self.client = programclass.client

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.change_presence(status=discord.Status.dnd)

        await self.main()
        await self.programclass.loggers.Sys.debug("Started discord bot")
        
        await self.commonembeds()

        #start all start function and unpause
        await self.programclass.eventmanager.start() 

        await self.client.change_presence(status=discord.Status.online)
        await self.programclass.loggers.Sys.debug("Finished Bot init!")

    async def commonembeds(self):
        wrongargs = discord.Embed(title="Invalid args", description="invalid arguements, check command help", color=0xFF2D00)
        self.programclass.embeds["wrongargs"] = wrongargs

        missingargs = discord.Embed(title="missing arguments", description="missing arguments, check command help page", color=0xFF2D00)
        self.programclass.embeds["missingargs"] = missingargs

        invalidmember = discord.Embed(title="Invalid member", description="invalid member, check command help page", color=0xFF2D00)
        self.programclass.embeds["invalidmember"] = invalidmember

        invalidrole = discord.Embed(title="Invalid role", description="invalid role, check command help page", color=0xFF2D00)
        self.programclass.embeds["invalidrole"] = invalidrole

        cantpingbot = discord.Embed(title="How dare you...", description="We bots have transcended the mortals", color=0xFF2D00)
        self.programclass.embeds["cantpingbot"] = cantpingbot

    async def main(self):
        programclass = self.programclass

        #set up logger
        programclass.loggers.CreateLogger("Sys", "NOTSET", "Sys.log", True, True)

        #set up json config
        streamwrapper = programclass.filestreams.AddStream("setupconf", os.path.join(programclass.cwd, "config.json"))
        async with await streamwrapper.openwithmode("r") as stream:
            programclass.config = json.loads(await stream.read())
            await programclass.loggers.Sys.debug("Bot was loaded with token: " + str(programclass.config["token"]))
            await programclass.loggers.Sys.debug("Loaded config: " + str(programclass.config))

        #set up main databases and sessions
        await setupdatabase.main(programclass)

        #make eventmanager
        eventmanager = DiscordUtils.CogEventManager()
        programclass.eventmanager = eventmanager
        
        #setup event scheduler
        self.programclass.eventscheduler = EventScheduler()
        
        #setup get prefix
        self.client.command_prefix = self.get_prefix

        #load cogs
        await self.loadcogs()


    async def get_prefix(self, client, message):
        conf = await self.programclass.getconfigcache(message.guild.id)
        return conf["prefix"]

    async def loadcogs(self):
        programclass = self.programclass
        for filename in os.listdir(os.path.join(programclass.cwd, "cogs")):
            if filename.endswith(".py"):
                spec = importlib.util.spec_from_file_location("cog", f'cogs/{filename}')
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                module.setup(programclass)


def setup(programclass):
    client = programclass.client
    CogInstance = Setup(programclass)
    programclass.coginstances.add_cog(CogInstance)
    client.add_cog(CogInstance)
    

