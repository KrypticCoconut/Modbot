import discord
import inspect
from discord.ext.commands.core import Command
from discord.ext.commands.context import Context
class DiscordUtils:

    @classmethod
    def helpargs(cls, desc=None, usage=None, hidden=False, shortdesc=None, showsubcat=False): #highly rigged function to assign function attributes as a decorator
        def wrapper(obj):
            obj.desc = desc
            obj.usage = usage
            obj.hidden = hidden
            obj.showsubcat=showsubcat
            if(not shortdesc):
                obj.shortdesc = desc
            else:
                obj.shortdesc = shortdesc
            return obj
        return wrapper

    class CogEventManager:
        def __init__(self):
            #self._paused = True
            self.startfuncs = dict()
            #self.events = list()

        # @property
        # def paused(self):
        #     return self._paused
        
        # @paused.setter
        # def paused(self, value:bool):
        #     self._paused = value
        #     #self.updatevents()

        @classmethod
        def startfunc(cls, func):
            func.startmethod = True
            return func

        # @classmethod
        # def waitforstart(cls, func):
        #     embed = discord.Embed(title="Patience child..", description="Command data is still loading", color=0xFF2D00)
        #     async def wrapper(self, ctx, *args):
        #         if(wrapper.pausevar):
        #             # for x in args:
        #             #     if(isinstance(x, Context)):
        #             #         await x.channel.send(embed=embed)
        #             #         return
        #             # for x in kwargs:
        #             #     if(isinstance(x, Context)):
        #             #         await x.channel.send(embed=embed)
        #             #         return
        #             pass
        #         try:
        #             await func(self, ctx, *args)
        #         except Exception as error:
        #             print(error) 
        #     wrapper.waitforstart = True
        #     return wrapper

        def inject(self, cog, coginstance):
            attrs = (getattr(cog, name) for name in dir(cog))
            startfuncs = filter(lambda x: callable(x) and getattr(x, "startmethod", False) , attrs)
            for method in startfuncs:
                self.startfuncs[method] = coginstance

            # commands = filter(lambda x: getattr(x.callback, "waitforstart", False) , cog.__cog_commands__)
            # for command in commands:
            #     command.callback.pausevar = self.paused
            #     self.events.append(command.callback)
        
        async def start(self):
            for func, instance in self.startfuncs.items():
                await func(instance)
            #self.paused = False 

        # def updatevents(self):
        #     for method in self.events:
        #         method.pausevar = self.paused
