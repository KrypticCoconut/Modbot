import discord
from discord.ext import commands

class ServerManagement(commands.Cog):
    
    def __init__(self, programclass):
        self.programclass = programclass
        self.client = programclass.client
    
    @commands.command()
    async def ping(self, ctx):
        await ctx.send('Pong! {0}'.format(round(self.client.latency, 1)))

def setup(programclass):
    client = programclass.client
    CogInstance = ServerManagement(programclass)
    programclass.coginstances.add_cog(CogInstance)
    client.add_cog(CogInstance)
        