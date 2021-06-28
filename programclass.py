import os

from Tools.Misc import FuncUtils
from Tools.logger import Loggers
from Tools.files import FileStreams
from Tools.sql import sqlconnmanager
import discord
from discord.ext import commands
from models import Base, ModBotTable


# program class that stores some variables and cog instances for easy accessability of data
# will also put some methods here later

class ProgramClass:
    def __init__(self, cwd: str, client: commands.Bot) -> None:
        if((er := FuncUtils.checkargs(["cwd", "client", "config"])) != None):
            raise Exception(er)
        self.cwd = cwd
        self.client = client
        self.coginstances = Cogs()
        self.config = dict() 

        self.cache = None
        self.loggers = Loggers(os.path.join(cwd, "data/logs"))
        self.filestreams = FileStreams()
        self.sqlconnection = None
        self.eventmanager = None


class Cogs:
    def __init__(self):
        self.all_cogs = dict()
    
    def add_cog(self,  cog: type):
        res = [x for key, val in self.all_cogs.items() if key == type(cog)]
        if(res):
            raise Exception("cannot have cogs with same name")
        self.all_cogs[cog.__class__.__name__] = cog

    def find_cog(self, cogname: str) -> [type, None]:
        res = [x for key, val in self.all_cogs.items if key == cogname]
        if res:
            return res
        return None
    
