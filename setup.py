import discord
from programclass import ProgramClass
import atexit
from discord.ext import commands
import asyncio
import os
import nest_asyncio
import pathlib
import signal
import json
from Tools.cache import ConfigCache
import setupdatabase
import models
import setupdatabase
from Tools.dpy import DiscordUtils
import importlib
import setupcog


intents = discord.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)
client.remove_command('help')
cwd = '/'.join(str(pathlib.Path(__file__).parent.absolute()).split("/"))
programclass = ProgramClass(cwd, client)
setupcog.setup(programclass)
client.run(json.loads(open("config.json","r").read())["token"])