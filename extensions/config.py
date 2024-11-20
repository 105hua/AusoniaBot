# ----------------------------------------------------------#
# Licensed under the GNU Affero General Public License v3.0 #
# ----------------------------------------------------------#

# pylint: disable=E1101

import discord
from discord.ext import commands
from modules import database_utils, configuration

CORE_CONF = configuration.CoreConfiguration()

CONFIG_OPTIONS = {
    "Moderator Role ID": "MODERATOR_ROLE_ID",
    "Diffusion Role ID": "DIFFUSION_ROLE_ID"
}


async def get_roles(ctx: discord.AutocompleteContext):
    choice = ctx.options["config_option"]
    if choice in ("Moderator Role ID", "Diffusion Role ID"):
        ac_array = []
        for role in ctx.interaction.guild.roles:
            if role.name != "@everyone":
                ac_array.append(role.name)
        return ac_array
    return None

class ConfigCommands(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.slash_command(
        name="setupserver",
        description="Set your server up for use with Ausonia!",
        guild_ids=[CORE_CONF.server_id]
    )
    @discord.option(
        name="moderator_role",
        description="The role Moderators in your Server.",
        type=discord.SlashCommandOptionType.role
    )
    @discord.option(
        name="diffusion_role",
        description="The role for the Diffusion Commands in your Server.",
        type=discord.SlashCommandOptionType.role
    )
    @commands.guild_only()
    async def setupserver(self, ctx: discord.ApplicationContext, moderator_role: discord.Role,
                          diffusion_role: discord.Role):
        if str(ctx.author.id) != str(CORE_CONF.owner_id):
            not_owner_embed = discord.Embed(
                title=":warning: You are not the set owner for this instance!",
                description="Your User ID does not match the Owner ID set for this instance. If you are the owner of "
                            "this instance of Ausonia, please ensure that you have correctly set the Owner ID in "
                            "your Core Configuration."
            )
            await ctx.respond(embed=not_owner_embed)
            return
        setup_success = database_utils.add_server_config(ctx.guild.id, moderator_role.id, diffusion_role.id)
        if setup_success:
            success_embed = discord.Embed(
                title=":white_check_mark: You've successfully set up Ausonia!",
                description="This server has been successfully added to this instance's database!"
            )
            await ctx.respond(embed=success_embed)
        else:
            failure_embed = discord.Embed(
                title=":warning: Something went wrong.",
                description="An error occurred when we tried to set this server up. Perhaps this server has already "
                            "been setup with this instance?"
            )
            await ctx.respond(embed=failure_embed)

    @commands.slash_command(
        name="editconfig",
        description="Edit your servers configuration.",
        guild_ids=[CORE_CONF.server_id]
    )
    @discord.option(
        name="config_option",
        description="The configuration entry you'd like to edit.",
        choices=CONFIG_OPTIONS.keys()
    )
    @discord.option(
        name="new_value",
        description="The value you'd like to set the configuration option to.",
        type=discord.SlashCommandOptionType.string,
        autocomplete=discord.utils.basic_autocomplete(get_roles)
    )
    @commands.guild_only()
    async def editconfig(self, ctx: discord.ApplicationContext, config_option: str, new_value: str):
        if ctx.author.id != CORE_CONF.owner_id:
            not_owner_embed = discord.Embed(
                title=":warning: You are not the Owner of this instance!",
                description="If you wish to obtain information from this command, please ask the Owner of this "
                            "instance."
            )
            await ctx.respond(embed=not_owner_embed)
            return
        if ctx.guild is None: # This should never run but the case is covered, in case it does.
            await ctx.respond("This command can only be ran in servers!")
            return
        selected_role = None
        for role in ctx.guild.roles:
            if role.name == new_value:
                selected_role = role
                break
        if selected_role is None:
            no_role_embed = discord.Embed(
                title=":warning: Couldn't find that role",
                description="That role does not seem to exist in this server."
            )
            await ctx.respond(embed=no_role_embed)
            return
        server_config = database_utils.get_server_config(ctx.guild.id)
        if server_config is None:
            no_config_embed = discord.Embed(
                title=":warning: No Config for this Server!",
                description="This server does not appear to have a config in our database. If you are the owner "
                            "of this instance and you'd like to create one, run `/setupserver`."
            )
            await ctx.respond(embed=no_config_embed)
            return
        server_config[CONFIG_OPTIONS[config_option]] = str(selected_role.id)
        update_success = database_utils.update_server_config(ctx.guild.id, server_config)
        if update_success:
            success_embed = discord.Embed(
                title=":white_check_mark: Update Success!",
                description="Your configuration has been successfully updated!"
            )
            await ctx.respond(embed=success_embed)
        else:
            failure_embed = discord.Embed(
                title=":warning: We couldn't update your configuration.",
                description="The bot was not able to update your configuration. Perhaps the Database is "
                            "down?"
            )
            await ctx.respond(embed=failure_embed)

    @commands.slash_command(
        name="serverconfig",
        description="Get this servers configuration (Owner Only).",
        guild_ids=[CORE_CONF.server_id]
    )
    @commands.guild_only()
    async def serverconfig(self, ctx: discord.ApplicationContext):
        if ctx.author.id != CORE_CONF.owner_id:
            not_owner_embed = discord.Embed(
                title=":warning: You are not the Owner of this instance!",
                description = "If you wish to obtain information from this command, please ask the Owner of this "
                              "instance."
            )
            await ctx.respond(embed=not_owner_embed)
            return
        server_config = database_utils.get_server_config(ctx.guild.id)
        moderator_role = None
        diffusion_role = None
        for role in ctx.guild.roles:
            if str(role.id) == server_config["MODERATOR_ROLE_ID"]:
                moderator_role = role
            if str(role.id) == server_config["DIFFUSION_ROLE_ID"]:
                diffusion_role = role
        config_embed = discord.Embed(
            title=f"Server Configuration for `{ctx.guild.name}`",
            description=f"""
            Server ID: `{ctx.guild.id}`
            Moderator Role Name: `{'Not Set' if moderator_role is None else moderator_role.name}`
            Moderator Role ID: `{'Not Set' if moderator_role is None else moderator_role.id}`
            Diffusion Role Name: `{'Not Set' if diffusion_role is None else diffusion_role.name}`
            Diffusion Role ID: `{'Not Set' if diffusion_role is None else diffusion_role.id}`
            """
        )
        await ctx.respond(embed=config_embed)

def setup(bot):
    bot.add_cog(ConfigCommands(bot))
