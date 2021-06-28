import discord
from discord.ext import commands
from Tools.dpy import DiscordUtils


@DiscordUtils.helpargs(desc="Utility commands", usage=None)
class Utility(commands.Cog):
    def __init__(self, programclass):
        self.eventmanager = programclass.eventmanager
        self.programclass = programclass
        self.client = programclass.client
        self.compiledhelp = dict()
        #self.ping = eventmanager.eventwrapper(self.ping)

        self.start = self.eventmanager.startfunc(self.start)

    async def start(self):
        await self.programclass.loggers.Sys.debug("Loaded Cog \"Utility\"")
        await self.compilehelp()

    async def compilehelp(self):
        # Compile args
        noneembed = discord.Embed(title="Help", color=0xEE8700)
        nonestring = ""
        for name,cog in self.programclass.coginstances.all_cogs.items():
            if(cog.hidden):
                continue
            nonestring += "{}: {}\n".format(name,cog.desc)
            cogembed = discord.Embed(title="Help", color=0xEE8700)
            cogstring = ""
            for command in cog.__cog_commands__:
                if(command.hidden):
                    continue
                cogstring += "{}: {}\n".format(command.name, getattr(cog.__class__, command.name).desc)
                commandembed = discord.Embed(title=command.name, color=0xEE8700)
                commandembed.add_field(name="Description:", value="```{}```".format(getattr(cog.__class__, command.name).desc), inline=False)
                commandembed.add_field(name="Usage:", value="```{}```".format(getattr(cog.__class__, command.name).usage), inline=False)
                self.compiledhelp["{} {}".format(name, command.name)] = commandembed
            cogembed.add_field(name="Commands in {}:".format(name), value="```{}```".format(cogstring))
            self.compiledhelp["{} None".format(name)] = cogembed
        noneembed.add_field(name="Command categories:", value="```{}```".format(nonestring))
        self.compiledhelp["None None"] = noneembed




    
    @DiscordUtils.helpargs(desc="Shows command usage", usage="""
help - shows all command categories
help \{category\} - shows commands in category
help \{category\} \{command\} - shows usage for specific command""")
    @commands.command()
    async def help(self, ctx, cog=None, command=None):
        if(e := self.eventmanager.ispaused()):
            await ctx.send(embed=e)
            return
        arg = "{} {}".format(cog, command)
        e = self.compiledhelp.get(arg)
        if(e == None):
            errembed = discord.Embed(title="Error", color=0xFF2D00)
            
            if(len(arg.split()) == 2):
                errembed.add_field(name="Command error", value="No command with name \"{}\" found in \"{}\" ".format(command, cog))
            else:
                errembed.add_field(name="Command error", value="No category found with name \"{}\"".format(cog))
            
            await ctx.send(embed=errembed)
            return
        await ctx.send(embed=e)
    

    @DiscordUtils.helpargs(desc="insane!", usage=None)
    @commands.command()
    async def ping(self, ctx):
        await ctx.send('Pong! {0} ms'.format(round(self.client.latency, 6)))

    @DiscordUtils.helpargs(desc="Utility commands", usage=None)
    @commands.command()
    async def serverinfo(self, ctx):
        """Shows server info"""

        server = ctx.message.guild

        roles = str(len(server.roles))
        emojis = str(len(server.emojis))
        channels = str(len(server.channels))

        embeded = discord.Embed(title=server.name, description='Server Info', color=0xEE8700)
        embeded.set_thumbnail(url=server.icon_url)
        embeded.add_field(name="Created on:", value=server.created_at.strftime('%d %B %Y at %H:%M UTC+3'), inline=False)
        embeded.add_field(name="Server ID:", value=server.id, inline=False)
        embeded.add_field(name="Users on server:", value=server.member_count, inline=True)
        embeded.add_field(name="Server owner:", value=server.owner, inline=True)

        embeded.add_field(name="Server Region:", value=server.region, inline=True)
        embeded.add_field(name="Verification Level:", value=server.verification_level, inline=True)

        embeded.add_field(name="Role Count:", value=roles, inline=True)
        embeded.add_field(name="Emoji Count:", value=emojis, inline=True)
        embeded.add_field(name="Channel Count:", value=channels, inline=True)

        await ctx.channel.send(embed=embeded) 


def setup(programclass):
    client = programclass.client
    CogInstance = Utility(programclass)
    programclass.coginstances.add_cog(CogInstance)
    client.add_cog(CogInstance)
    

