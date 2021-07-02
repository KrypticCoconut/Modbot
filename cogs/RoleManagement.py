import discord
from discord.ext import commands
from Tools.dpy import DiscordUtils
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
            mutedRole = await guild.create_role(name=name, colour=discord.Colour.darker_grey())
            for channel in guild.channels:
                await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_messages=True)
            return mutedRole
        else:
            return mutedRole

    async def mute_member(self, guild: discord.Guild, member: discord.Member):
        conf = await self.programclass.getconfigcache(guild.id)
        if(conf["default_mute_role"] == None):
            muterole = self.create_muted()
        else:
            try:
                guild.get_role(conf["default_mute_role"])
            except RoleNotFound:
                embed = discord.Embed(title="Unkown mute role", description="invalid mute role, use `setmuterole` command to set new role", color=0xFF2D00)

    @DiscordUtils.helpargs(hidden=True, showsubcat=False,
    shortdesc="used to set muterole",
    desc="""changes/gets the default mute role, this role is current used by the following commands:
-warn
""",
    usage="""
muterole set {role} - set the mute role to specified role
muterole get - get current mute role
""")
    @commands.group(name="muterole", invoke_without_command=True)
    async def muterole(self, ctx, *args):
        if(args):
            await ctx.channel.send(embed=self.programclass.embeds["wrongargs"])
        else:
            await ctx.channel.send(embed=self.programclass.embeds["missingargs"])
    
    @DiscordUtils.helpargs(hidden=True)
    @muterole.command(name="set")
    async def muterole_set(self, ctx, role: discord.Role):
        conf = await self.programclass.getconfigcache(ctx.guild.id)
        conf["default_mute_role"] = role.id
        embed = discord.Embed(title="Success!", description="changed default muted role to {}".format(role.mention), color=0x00C166)
        await ctx.channel.send(embed=embed)

    @muterole_set.error
    async def muterole_set_error(self, ctx, error):
        if(isinstance(error, RoleNotFound)):
            await ctx.channel.send(embed=self.programclass.embeds["invalidrole"])
        elif(isinstance(error, MissingRequiredArgument)):
            await ctx.channel.send(embed=self.programclass.embeds["missingargs"])

    @DiscordUtils.helpargs(hidden=True)
    @muterole.command(name="get")
    async def muterole_get(self, ctx):
        conf = await self.programclass.getconfigcache(ctx.guild.id)
        r = conf["default_mute_role"]
        role = discord.utils.get(ctx.guild.roles, id=r)
        if(role):
            role = role.mention
        embed = discord.Embed(title="Default muted role:", description="{}".format(role), color=0x00C166)
        await ctx.channel.send(embed=embed)


def setup(programclass):
    client = programclass.client
    CogInstance = RoleManagement(programclass)
    programclass.eventmanager.inject(RoleManagement, CogInstance)
    programclass.coginstances.add_cog(CogInstance)
    client.add_cog(CogInstance)
    

