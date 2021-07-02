import discord
from discord.ext import commands
from Tools.dpy import DiscordUtils
from discord.ext.commands.errors import *
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import datetime
import asyncio



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


    @DiscordUtils.helpargs(hidden=True, showsubcat=False,
    shortdesc="mutes a member",
    desc="""Mutes a member for said amount of time
NOTE: by default this command will create a new Muted role or use any role with the name "Muted", but it can be changed by using the `muterole` command in the `RoleManagement` category
""",
    usage="""mute add {member} - mute member
mute add {member} {time} - mute member for given time, (time must be in `Days-Hours-Minutes-Seconds` format)
mute show - shows all scheduled timers for mutes
mute remove {member} - basically cancels timer for unmute #using this command is basically gods work, it reduces server stress
""")
    @commands.group(name="mute", showsubcat=False, invoke_without_command=True)
    async def mute(self, ctx, *args):
        if(args):
            await ctx.channel.send(embed=self.programclass.embeds["wrongargs"])
        else:
            await ctx.channel.send(embed=self.programclass.embeds["missingargs"])

    @DiscordUtils.helpargs(hidden=True)
    @mute.command(name="add")
    async def mute_add(self, ctx, member: discord.Member, time=None):
        if(member.bot):
            await ctx.channel.send(embed=self.programclass.embeds["cantpingbot"])
        embed = discord.Embed(title="Success!", description="Muted {}".format(member.name), color=0x00C166)
        conf = await self.programclass.getconfigcache(ctx.guild.id)
        if(time):
            try:
                if(len(time) > 90):
                    embed = discord.Embed(title="Error!", description="Too long time string".format(member.name), color=0x00C166)
                    await ctx.channel.send(embed=embed)
                    return
                day, hour, minutes, seconds = map(int, time.split('-'))
                time = datetime.datetime.now() + datetime.timedelta(days=day, hours=hour, minutes=minutes, seconds=seconds)
                self.programclass.eventscheduler.AddEvent(conf, member, time, self.unmute_member, [ctx.guild.id, member.id])
                embed.set_footer(text="User will be unmuted at {}".format(self.programclass.eventscheduler.GetDateTime(time)))
            except:
                await ctx.channel.send(embed=self.programclass.embeds["wrongargs"])
                return

        new, muterole = await self._get_muterole(conf, ctx.guild)
        if(new):
            embed.add_field(name="Note:",value="none\invalid default mute role, created\set it to a new mute role, use command `muterole get` to get new default muterole", inline=False)
        await member.add_roles(muterole)
        await ctx.channel.send(embed=embed)

    async def unmute_member(self, serverid, member_id):
        try:
            guild = self.client.get_guild(serverid)
        except:
            #guild kicked bot
            return
        try:
            member = guild.get_member(member_id)
        except:
            #member left
            return

        conf = await self.programclass.getconfigcache(serverid)
        # if(not conf["default_mute_role"]):
        #     #no default role set
        #     return

        role = guild.get_role(conf["default_mute_role"])
        if(not role):
            #role not found
            conf["default_mute_role"] = None
            return
        if(role):
            await member.remove_roles(role)

        conf = await self.programclass.getconfigcache(serverid)
        m = [m for m in conf["members"] if m["member_id"] == member_id][0]
        m["job"] = None


    @mute_add.error
    async def mute_add_error(self, ctx, error):
        if(isinstance(error, MemberNotFound)):
            await ctx.channel.send(embed=self.programclass.embeds["invalidmember"])
        elif(isinstance(error, MissingRequiredArgument)):
            await ctx.channel.send(embed=self.programclass.embeds["missingargs"])

    @DiscordUtils.helpargs(hidden=True)
    @mute.command(name="show")
    async def mute_show(self, ctx):
        eventstr = str()
        conf = await self.programclass.programclass.getconfigcache(ctx.guild.id)
        delete = list()
        for i, member in enumerate(conf["members"]):
            if(not (m := ctx.guild.get_member(member["member_id"]))):
                delete.append(i)
                continue
            if(j := member.get("job")):
                eventstr += "{}, {}".format(m, j["datetime"])
        if(eventstr == ""):
            eventstr = "None"
        embed = discord.Embed(title="Active unmute schedules: ", description="```{}```".format(eventstr), color=0x00C166)
        await ctx.channel.send(embed=embed)

    @DiscordUtils.helpargs(hidden=True)
    @mute.command(name="remove")
    async def mute_remove(self, ctx, member:discord.Member):

        conf = await self.programclass.getconfigcache(ctx.guild.id)
        m = [m for m in conf["members"] if m["member_id"] == member.id]
        if(not m):
            embed = discord.Embed(title="Error", description="User does not have a unmute schedule", color=0xFF2D00)
        else:
            m = m[0]
            if(not (j := m.get("job"))):
                embed = discord.Embed(title="Error", description="User does not have a unmute schedule", color=0xFF2D00)
            else:
                self.programclass.eventscheduler.scheduler.remove_job(j["jobid"])
                m["job"] = None
                embed = discord.Embed(title="Success", description="Job successfully unregistered", color=0x00C166)
        await ctx.channel.send(embed=embed)

    # @mute_remove.error
    # async def mute_remove_error(self, ctx, error):
    #     if(isinstance(error, MissingRequiredArgument)):
    #         await ctx.channel.send(embed=self.programclass.embeds["missingargs"])
    #     if(isinstance(error, MemberNotFound)):
    #         await ctx.channel.send(embed=self.programclass.embeds["invalidmember"])


    @DiscordUtils.helpargs(
        desc="Group of subcommands used to warn/strike members", showsubcat=True,
        usage="""
help {category} warn - displays all subcommands
help {category} warn {subcommand} - shows help for subcommand
""")
    @commands.group(name="warn", invoke_without_command=True)
    async def warn(self, ctx, *args):
        subcommands = list()
        if(args):
            await ctx.channel.send(embed=self.programclass.embeds["wrongargs"])
            return
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
        conf = await self.programclass.getconfigcache(ctx.guild.id)
        conf["default_warns"] = warns
        embed = discord.Embed(title="Success!", description="defaultwarns set to {}".format(warns), color=0x00C166)
        await ctx.channel.send(embed=embed)

    @setdefaultwarns.error
    async def setdefaultwarns_error(self, ctx, error):
        if(isinstance(error, MissingRequiredArgument)):
            await ctx.channel.send(embed=self.programclass.embeds["missingargs"])

    @DiscordUtils.helpargs(hidden=True, 
    shortdesc="Warn/srike a member",
    desc="""Warns the member and take out one left warn, when a member has 0 left warns, they will be muted on thier next warn
NOTE: by default this command will create a new Muted role or use any role with the name "Muted", but it can be changed by using the `muterole` command in the `RoleManagement` category""",
    usage="warn warnuser {@user} {reason}")
    @warn.command(name="warnuser")
    async def warnuser(self, ctx, member:discord.Member, reason=None):
        if(member.bot):
            await ctx.channel.send(embed = self.programclass.embeds["cantpingbot"])
            return
        conf = await self.programclass.getconfigcache(ctx.guild.id)
        mute, warnsleft = await self._warn(conf, member.id)
        if(warnsleft < 0):
            embed = discord.Embed(title="Error", color=0xFF2D00, description="No warns left for {}".format(member.display_name))
            await ctx.channel.send(embed=embed)
            return
        embed = discord.Embed(title="Success!", color=0x00C166)
        embed.add_field(name="Warned {}".format(member.name), value="Reason: {}".format(reason), inline=True)
        if(mute):
            new, muterole = await self._get_muterole(conf, ctx.guild)
            if(new):
                embed.add_field(name="Note:",value="invalid default mute role, created\set it to a new mute role, use command `muterole get` to get new muterole", inline=False)
            await member.add_roles(muterole)
            embed.set_footer(text="Warnings remaining: -1(user muted)")
        else:
            embed.set_footer(text="Warnings remaining: {}".format(warnsleft))
        await ctx.channel.send(embed=embed)
    
    @warnuser.error
    async def warnuser_error(self, ctx, error):
        if(isinstance(error, MemberNotFound)):
            await ctx.channel.send(embed=self.programclass.embeds["invalidmember"])
        elif(isinstance(error, MissingRequiredArgument)):
            await ctx.channel.send(embed=self.programclass.embeds["missingargs"])

    @DiscordUtils.helpargs(hidden=True, 
    shortdesc="Get remaining warns left for a user",
    desc="returns remaining warns left for a user",
    usage="warn getwarns {@user}")
    @warn.command(name="getwarns")
    async def getwarns(self, ctx, member: discord.User):
        if(member.bot):
            await ctx.channel.send(embed = self.programclass.embeds["cantpingbot"])
            return
        conf = await self.programclass.getconfigcache(ctx.guild.id)
        indice  = [i for i,x in enumerate(conf["members"]) if x["member_id"] == member.id]
        if(not indice):
            left = conf["default_warns"]
        else:
            left = conf["members"][indice]["warnsleft"]
        if(left < 0):
            left = "{}(user muted)".format(left)
        embed = discord.Embed(title="Warns left for {}".format(member.name), description = "{}".format(left) ,color=0x00C166)
        await ctx.channel.send(embed=embed)

    @getwarns.error
    async def getwarns_error(self, ctx, error):
        if(isinstance(error, MemberNotFound)):
            await ctx.channel.send(embed=self.programclass.embeds["invalidmember"])
        elif(isinstance(error, MissingRequiredArgument)):
            await ctx.channel.send(embed=self.programclass.embeds["missingargs"])

    @DiscordUtils.helpargs(hidden=True, 
    shortdesc="Give user extra warns",
    desc="Adds 1 extra warn to a member",
    usage="warn addwarn {@user}")
    @warn.command(name="addwarn")
    async def addwarn(self, ctx, member: discord.User):
        if(member.bot):
            await ctx.channel.send(embed = self.programclass.embeds["cantpingbot"])
            return
        conf = await self.programclass.getconfigcache(ctx.guild.id)
        indice  = [i for i,x in enumerate(conf["members"]) if x["member_id"] == member.id]
        if(not indice):
            now = conf["default_warns"]+1
            conf["members"].append({"member_id": member.id, "warnsleft": now})   
        else:
            now = conf["members"][indice]["default_warns"] + 1
            conf["members"][indice]["default_warns"] = now
        embed = discord.Embed(title="Added one warn for {}".format(member.name), description = "warns now: {}".format(now) ,color=0x00C166)
        await ctx.channel.send(embed=embed)

    @getwarns.error
    async def addwarn_error(self, ctx, error):
        if(isinstance(error, MemberNotFound)):
            await ctx.channel.send(embed=self.programclass.embeds["invalidmember"])
        elif(isinstance(error, MissingRequiredArgument)):
            await ctx.channel.send(embed=self.programclass.embeds["missingargs"])


    async def _warn(self, conf, userid):

        indice  = [i for i,x in enumerate(conf["members"]) if x["member_id"] == userid]
        if(not indice):
            conf["members"].append({"member_id": userid, "warnsleft": conf["default_warns"]-1})     
            return conf["default_warns"]-1==-1, conf["default_warns"]-1
        else:
            indice = indice[0]
            currentwarns = conf["members"][indice]["warnsleft"]
            if(currentwarns == 0):
                conf["members"][indice]["warnsleft"] = currentwarns-1    
                return True, 0
            else:
                conf["members"][indice]["warnsleft"] = currentwarns-1    
                return False, currentwarns-1
    
    async def _get_muterole(self, conf, guild):
        muteroleid = conf["default_mute_role"]
        if(muteroleid):
            muterole = discord.utils.get(guild.roles, id=muteroleid)
            if(not muterole):
                muterole = await self.programclass.coginstances.all_cogs["RoleManagement"].create_muted(guild, "Muted")
                conf["default_mute_role"] = muterole.id
                #LOG MUTED ROLE HERE
                return True, muterole
            else:
                return False, muterole
        else:
            muterole = await self.programclass.coginstances.all_cogs["RoleManagement"].create_muted(guild, "Muted")
            conf["default_mute_role"] = muterole.id
            #LOG MUTED ROLE HERE
            return True, muterole

    @DiscordUtils.helpargs(hidden=True)
    @commands.command(name="getconfig")
    async def getconfig(self, ctx):
        conf = await self.programclass.getconfigcache(ctx.guild.id)
        await ctx.channel.send(conf)

def setup(programclass):
    client = programclass.client
    CogInstance = UserManagement(programclass)
    programclass.eventmanager.inject(UserManagement, CogInstance)
    programclass.coginstances.add_cog(CogInstance)
    client.add_cog(CogInstance)
    #print(UserManagement.test.callback.pausevar)