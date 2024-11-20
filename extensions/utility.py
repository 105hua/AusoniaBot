# ----------------------------------------------------------#
# Licensed under the GNU Affero General Public License v3.0 #
# ----------------------------------------------------------#

import time
import datetime
import aiofiles
import discord
from discord.ext import commands
from modules import configuration, logging_utils

CORE_CONF = configuration.CoreConfiguration()
LOGGER = logging_utils.Logger()

def format_time(epoch: int) -> str:
    return datetime.datetime.fromtimestamp(epoch).strftime("%H:%M")

def get_latency_emoji(latency: int) -> str:
    if latency <= 200:
        return ":green_circle:"
    if 201 <= latency <= 500:
        return ":yellow_circle:"
    return ":red_circle:"

class UtilityCommands(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.afk_members = []

    @commands.slash_command(
        name="serverinfo",
        description="Get some information about this server.",
        guild_ids=[CORE_CONF.server_id]
    )
    async def serverinfo(self, ctx: discord.ApplicationContext):
        member_count = ctx.guild.member_count
        server_name = ctx.guild.name
        info_embed = discord.Embed(
            title="Server Information",
            description=f"**Server Name:** `{server_name}`\n**Member Count:** `{member_count}`"
        )
        await ctx.respond(embed=info_embed)

    @commands.slash_command(
        name="worldtime",
        description="Wondering what the time is around the world? Find out by running this command!",
        guild_ids=[CORE_CONF.server_id]
    )
    async def worldtime(self, ctx: discord.ApplicationContext):
        utc_epoch = datetime.datetime.now(datetime.UTC).timestamp()
        la_epoch = int(utc_epoch - (8 * 3600))  # Los Angeles
        nyc_epoch = int(utc_epoch - (5 * 3600))  # New York
        pa_epoch = int(utc_epoch + 3600)  # Paris
        mo_epoch = int(utc_epoch + (3 * 3600))  # Moscow
        du_epoch = int(utc_epoch + (4 * 3600))  # Dubai
        mu_epoch = int(utc_epoch + (5.5 * 3600))  # Mumbai
        be_epoch = int(utc_epoch + (8 * 3600))  # Beijing
        jp_epoch = int(utc_epoch + (9 * 3600))  # Tokyo
        syd_epoch = int(utc_epoch + 36000)  # Sydney
        world_time_embed = discord.Embed(
            title=":globe_with_meridians: What's the time around the world?",
            description=f"""
                    **Los Angeles, California:** `{format_time(la_epoch)}`
                    **New York City, New York:** `{format_time(nyc_epoch)}`
                    **London, England:** `{format_time(int(utc_epoch))}`
                    **Paris, France:** `{format_time(pa_epoch)}`
                    **Moscow, Russia:** `{format_time(mo_epoch)}`
                    **Dubai, United Arab Emirates:** `{format_time(du_epoch)}`
                    **Mumbai, India:** `{format_time(mu_epoch)}`
                    **Beijing, China:** `{format_time(be_epoch)}`
                    **Tokyo, Japan:** `{format_time(jp_epoch)}`
                    **Sydney, Australia:** `{format_time(syd_epoch)}`
                    """
        )
        await ctx.respond(embed=world_time_embed)

    @commands.slash_command(
        name="ping",
        description="Ping the bot and get the response time.",
        guild_ids=[CORE_CONF.server_id]
    )
    async def ping(self, ctx: discord.ApplicationContext):
        latency = round(ctx.bot.latency * 1000)
        ping_embed = discord.Embed(
            title=":electric_plug: Latency",
            description=f"{get_latency_emoji(latency)} `{latency}ms`"
        )
        await ctx.respond(embed=ping_embed)

    @commands.slash_command(
        name="uptime",
        description="Find out how long the Bot has been online for.",
        guild_ids=[CORE_CONF.server_id]
    )
    async def uptime(self, ctx: discord.ApplicationContext):
        try:
            current_timestamp = datetime.datetime.now().timestamp()
            async with aiofiles.open("start_time.txt", "r") as f:
                time_started = int(await f.read())
            time_difference = current_timestamp - time_started
            formatted_time = time.strftime("%Hhrs %Mmins %Ssecs", time.gmtime(time_difference))
            time_embed = discord.Embed(
                title=":robot: Bot Uptime",
                description=f"This bot has been online for `{formatted_time}`"
            )
            await ctx.respond(embed=time_embed)
        except (ValueError, IOError):
            failed_embed = discord.Embed(
                title=":warning: Failed to read Start Time",
                description="If you are the owner, please restart the bot and run this command again."
            )
            await ctx.respond(embed=failed_embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild.id != CORE_CONF.server_id or len(message.mentions) == 0:
            return
        mentioned_afk_members: list[discord.Member] = []
        for member in message.mentions:
            if member in self.afk_members:
                mentioned_afk_members.append(member)
        if len(mentioned_afk_members) == 0:
            return
        afk_message = "The following members that you've mentioned in your message are currently AFK:\n"
        for index, member in enumerate(mentioned_afk_members):
            afk_message += "- " + member.display_name
            if index != len(mentioned_afk_members):
                afk_message += "\n"
        await message.reply(afk_message)


    @commands.slash_command(
        name="afk",
        description="Toggle yourself as AFK so that when someone pings you, they get a message!"
    )
    async def afk(self, ctx: discord.ApplicationContext):
        if ctx.author in self.afk_members:
            self.afk_members.remove(ctx.author)
            back_embed = discord.Embed(
                title=":white_check_mark: Welcome Back!",
                description="You're no longer marked as AFK!"
            )
            await ctx.respond(embed=back_embed)
        else:
            self.afk_members.append(ctx.author)
            afk_embed = discord.Embed(
                title=":white_check_mark: See you soon!",
                description="You're now marked as AFK!"
            )
            await ctx.respond(embed=afk_embed)

    @commands.slash_command(
        name="commandcount",
        description="Get the number of commands in this bot!",
        guild_ids=[CORE_CONF.server_id]
    )
    async def commandcount(self, ctx: discord.ApplicationContext):
        command_count_embed = discord.Embed(
            title=":robot: Command Count",
            description=f"This bot has `{len(ctx.bot.commands)}` commands!"
        )
        await ctx.respond(embed=command_count_embed)

def setup(bot):
    bot.add_cog(UtilityCommands(bot))
