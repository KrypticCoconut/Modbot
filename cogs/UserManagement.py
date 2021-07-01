import discord
from discord.ext import commands
from Tools.dpy import DiscordUtils
from setupdatabase import addconfigcache, getconfigcache
from discord.ext.commands.errors import *

commands
@DiscordUtils.helpargs(desc="Commands to manage user permissions and warnings", usage=None)
class UserManagement(commands.Cog):
    def __init__(self, programclass):
        self.eventmanager = programclass.eventmanager
        self.programclass = programclass
        self.client = programclass.client
          #self.start = self.eventmanager.startfunc(self.start)

    @DiscordUtils.CogEventManager.startfunc
    async def start(self):
        await self.programclass.loggers.Sys.debug("Loaded Cog \"User Management\"")


    @DiscordUtils.helpargs(
        desc="Group of subcommands used to warn/strike members", 
        usage="""
help {category} warn - displays all subcommands
help {category} warn {subcommand} - shows help for subcommand
""")
    @commands.group(name="warn", invoke_without_command=False)
    async def warn(self, ctx):
        subcommands = list()
        for command in self.warn.commands:
            subcommands.append(command.name)
        subcommands = ", ".join(subcommands)
        embed = discord.Embed(title="Command Subcategory!", description="group of subcommands related to member warns/strikes, subcommands: {}".format(subcommands), color=0x00C166)
        await ctx.channel.send(embed=embed)
    


    @DiscordUtils.helpargs(hidden=True, 
    shortdesc="change default warn/strikes for members",
    desc="""changes the default number of warn/strikes a new member will have
NOTE: this does not reset when a member leaves and joins again""",
    usage="warn setdefaultwarns {warns} ")
    @warn.command(name="setdefaultwarns")
    async def setdefaultwarns(self, ctx, warns: int):
        if(not isinstance(warns, int)):
            embed = discord.Embed(title="Invalid args", description="\"warns\" argument has to be a number", color=0xFF2D00)
            await ctx.channel.send(embed=embed)
            return
        conf = await getconfigcache(ctx.guild.id)
        conf["default_warns"] = warns
        embed = discord.Embed(title="Success!", description="defaultwarns set to {}".format(warns), color=0x00C166)
        await ctx.channel.send(embed=embed)

    @setdefaultwarns.error
    async def setdefaultwarns_error(self, ctx, error):
        if(isinstance(error, MissingRequiredArgument)):
            await ctx.channel.send(embed=self.programclass.embeds["missingargs"])

    @DiscordUtils.helpargs(hidden=True, 
    shortdesc="Warn/srike a member",
    desc="Warns the member and take out one left warn, when a member has 0 left warns, they will be muted on thier next warn, if no default muted role is set (muterole in RoleManagement category) then this command will create a new muted role ",
    usage="warn warnuser {@user} {reason}")
    @warn.command(name="warnuser")
    async def warnuser(self, ctx, member:discord.Member, reason=None):
        if(member.bot):
            await ctx.channel.send(embed = self.programclass.embeds["cantpingbot"])
            return
        conf = await getconfigcache(ctx.guild.id)
        mute, warnsleft = await self._warn(conf, member.id)
        if(warnsleft < 0):
            embed = discord.Embed(title="Error", color=0xFF2D00, description="No warns left for {}".format(member.display_name))
            await ctx.channel.send(embed=embed)
            return
        embed = discord.Embed(title="Success!", color=0x00C166)
        embed.add_field(name="Warned {}".format(member.display_name), value="Reason: {}".format(reason), inline=True)
        if(mute):
            embed.set_footer(text="Warnings remaining: 0(user muted)")
        else:
            embed.set_footer(text="Warnings remaining: {}".format(warnsleft))
        await ctx.channel.send(embed=embed)
    
    @warnuser.error
    async def warnuser_error(self, ctx, error):
        if(isinstance(error, MemberNotFound)):
            await ctx.channel.send(embed=self.programclass.embeds["invalidmember"])
        elif(isinstance(error, MissingRequiredArgument)):
            await ctx.channel.send(embed=self.programclass.embeds["missingargs"])

    async def _warn(self, conf, userid):

        indice  = [i for i,x in enumerate(conf["members"]) if x["member_id"] == userid]
        if(not indice):
            conf["members"].append({"member_id": userid, "warnsleft": conf["default_warns"]-1})        
            return False, conf["default_warns"]-1
        else:
            indice = indice[0]
            currentwarns = conf["members"][indice]["warnsleft"]
            if(currentwarns-1 < 0):
                return True, -1
            else:
                conf["members"][indice]["warnsleft"] = currentwarns-1    
            if(currentwarns-1 == 0):
                return True, 0
            return False, currentwarns-1
    
    @DiscordUtils.helpargs(hidden=True)
    @commands.command(name="getconfig")
    async def getconfig(self, ctx):
        conf = await getconfigcache(ctx.guild.id)
        await ctx.channel.send(conf)

def setup(programclass):
    client = programclass.client
    CogInstance = UserManagement(programclass)
    programclass.eventmanager.inject(UserManagement, CogInstance)
    programclass.coginstances.add_cog(CogInstance)
    client.add_cog(CogInstance)
    #print(UserManagement.test.callback.pausevar)