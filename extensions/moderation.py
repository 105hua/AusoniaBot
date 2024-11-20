# ----------------------------------------------------------#
# Licensed under the GNU Affero General Public License v3.0 #
# ----------------------------------------------------------#

# pylint: disable=E1101

from datetime import datetime
import discord
from discord.ext import commands
from discord.ext.pages import Paginator, Page
from modules import configuration, database_utils

CORE_CONF = configuration.CoreConfiguration()

UNITS_IN_SECONDS = {
    's': 1,
    'm': 60,
    'h': 3600,
    'd': 86400,
    'w': 604800,
}

class ModerationCommands(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.slash_command(
        name="recentpunishments",
        description="Get the 5 most recent punishments for the server.",
        guild_ids=[CORE_CONF.server_id]
    )
    @commands.guild_only()
    async def recentpunishments(self, ctx: discord.ApplicationContext):
        if not database_utils.is_moderator(ctx.guild.id, ctx.author) and ctx.author.id != CORE_CONF.owner_id:
            invalid_permissions_embed = discord.Embed(
                title=":warning: Invalid Permissions",
                description="You do not have the correct permissions to view recent punishments in this server."
            )
            await ctx.respond(embed=invalid_permissions_embed)
            return
        punishments = database_utils.get_recent_punishments_for_server(ctx.guild.id)
        if punishments is None or punishments == []:
            no_punishments_embed = discord.Embed(
                title=":warning: No Punishments!",
                description="No one has been punished in this server... YET..."
            )
            await ctx.respond(embed=no_punishments_embed)
            return
        pages = []
        for index, punishment in enumerate(punishments):
            enforcer = self.bot.get_user(punishment[2])
            offender = self.bot.get_user(punishment[3])
            pages.append(
                Page(
                    embeds=[
                        discord.Embed(
                            title=f"Punishment #{index + 1}",
                            description=f"""
                            Punishment ID: `{punishment[0]}`
                            Server ID: `{punishment[1]}`
                            Enforcer Info: `{f'{enforcer.display_name} - ' if enforcer is not None else ''}{punishment[2]}`
                            Offender Info: `{f'{offender.display_name} - ' if offender is not None else ''}{punishment[3]}`
                            Issued: `{datetime.fromtimestamp(punishment[5]).strftime('%m/%d/%Y at %H:%M:%S')}`
                            Expires: `{datetime.fromtimestamp(punishment[6]).strftime('%m/%d/%Y at %H:%M:%S')}`
                            """
                        )
                    ]
                )
            )
        paginator = Paginator(pages=pages)
        await paginator.respond(ctx.interaction)

    @commands.slash_command(
        name="ban",
        description="Bans a Member",
        guild_ids=[CORE_CONF.server_id]
    )
    @discord.option(
        name="offender",
        description="The member you'd like to ban.",
        type=discord.SlashCommandOptionType.user
    )
    @discord.option(
        name="reason",
        description="The reason you'd like to ban the user for.",
        type=discord.SlashCommandOptionType.string
    )
    @discord.option(
        name="duration",
        description="The time you'd like to ban the user for. Examples are '1w', '7d' etc.",
        type=discord.SlashCommandOptionType.string
    )
    @commands.guild_only()
    async def ban(self, ctx: discord.ApplicationContext, offender: discord.Member, reason: str, duration: str):
        if not database_utils.is_moderator(ctx.guild.id, ctx.author):
            not_moderator_embed = discord.Embed(
                title=":warning: You are not a moderator!",
                description="Only moderators can run this command."
            )
            await ctx.respond(embed=not_moderator_embed)
            return
        duration_seconds = None
        # Get actual duration
        if duration.lower() == "forever":
            duration_seconds = 6307200000 # 200 Years
        else:
            try:
                number = int(duration[:-1])
                unit = duration[-1].lower()
                if unit not in UNITS_IN_SECONDS:
                    invalid_unit_embed = discord.Embed(
                        title=":warning: Invalid Unit Provided!",
                        description="Please choose a valid unit, like 'w' for weeks or 'm' for months."
                    )
                    await ctx.respond(embed=invalid_unit_embed)
                    return
                duration_seconds = number * UNITS_IN_SECONDS[unit]
            except (ValueError, IndexError):
                invalid_duration_embed = discord.Embed(
                    title=":warning: Invalid Duration Provided!",
                    description="Please choose a valid duration, like '1w' for 1 week."
                )
                await ctx.respond(embed=invalid_duration_embed)
                return
        # Ensure duration is no longer None
        if duration_seconds is None:
            duration_parse_error_embed = discord.Embed(
                title=":warning: Couldn't parse your duration!",
                description="We had a problem with parsing your duration on our end. If you see this message, please "
                            "contact the owner of this instance, or the developer."
            )
            await ctx.respond(embed=duration_parse_error_embed)
        # Proceed with the ban.
        await ctx.guild.ban(
            user=offender,
            delete_message_seconds=0,
            reason=reason
        )
        database_utils.create_punishment(
            ctx.guild.id,
            ctx.author.id,
            offender.id,
            f"KICK: {reason}",
            duration_seconds
        )
        ban_pushed_embed = discord.Embed(
            title=":white_check_mark: Ban Pushed!",
            description=f"You've successfully banned `{offender.display_name}`!"
        )
        await ctx.respond(embed=ban_pushed_embed)

def setup(bot):
    bot.add_cog(ModerationCommands(bot))
