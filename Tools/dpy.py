import discord

class DiscordUtils:

    @classmethod
    def helpargs(cls, desc=None, usage=None, example=None, hidden=False): #highly rigged function to assign function attributes as a decorator
        def wrapper(obj):
            obj.desc = desc
            obj.usage = usage
            obj.example = example
            obj.hidden = hidden
            return obj
        return wrapper

    class CogEventManager:
        def __init__(self):
            self.paused = True
            self.startfuncs = list()
            self.embed = discord.Embed(title="Patience child..", description="Command data is still loading", color=0xFF2D00)

        def ispaused(self):
            if(self.paused):
                return self.embed
            return None

        def startfunc(self, func):
            self.startfuncs.append(func)
            return func

        async def start(self):
            for func in self.startfuncs:
                await func()
            self.paused = False 