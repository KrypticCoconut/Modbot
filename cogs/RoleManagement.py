import discord
from discord.ext import commands
from Tools.dpy import DiscordUtils
from setupdatabase import addconfigcache, getconfigcache
from discord.ext.commands.errors import *

commands
@DiscordUtils.helpargs(desc="Commands to manage user permissions and warnings", usage=None)
class RoleManagement(commands.Cog):
    def __init__(self, programclass):
        self.eventmanager = programclass.eventmanager
        self.programclass = programclass
        self.client = programclass.client


    @DiscordUtils.CogEventManager.startfunc
    async def start(self):
        await self.programclass.loggers.Sys.debug("Loaded Cog \"Role Management\"")

    async def create_muted(self, guild, name):
        mutedRole = discord.utils.get(guild.roles, name=name)
        if(not mutedRole):
            mutedRole = await guild.create_role(name=name)
            for channel in guild.channels:
                await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True, read_messages=False)
            return mutedRole
        else:
            return mutedRole

    async def mute_member(self, guild: discord.Guild, member: discord.Member):
        conf = await getconfigcache(guild.id)
        if(conf["default_mute_role"] == None):
            muterole = self.create_muted()
        else:
            try:
                guild.get_role(conf["default_mute_role"])
            except RoleNotFound:
                embed = discord.Embed(title="Unkown mute role", description="invalid mute role, use `setmuterole` command to set new role", color=0xFF2D00)

    @DiscordUtils.helpargs(hidden=True)
    @commands.command(name="setmuterole")
    async def setmuterole(self, ctx, role: discord.Role):
        conf = await getconfigcache(ctx.guild.id)
        conf["default_mute_role"] = role.id
    
    @setmuterole.error
    async def setmuterole_error(self, ctx, error):
        if(isinstance(error, RoleNotFound)):
            await ctx.channel.send(embed=self.programclass.embeds["invalidrole"])
        elif(isinstance(error, MissingRequiredArgument)):
            await ctx.channel.send(embed=self.programclass.embeds["missingargs"])

def setup(programclass):
    client = programclass.client
    CogInstance = RoleManagement(programclass)
    programclass.eventmanager.inject(RoleManagement, CogInstance)
    programclass.coginstances.add_cog(CogInstance)
    client.add_cog(CogInstance)
    

