# ----------------------------------------------------------#
# Licensed under the GNU Affero General Public License v3.0 #
# ----------------------------------------------------------#

# pylint: disable=E1101

import discord
from discord.ext import commands
from modules import configuration, earthquake_utils

CORE_CONF = configuration.CoreConfiguration()

class EarthquakeCommands(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.quake_wrapper = earthquake_utils.EarthquakeWrapper()

    @commands.slash_command(
        name="earthquake",
        description="Get information on Earthquakes in Japan.",
        guild_ids=[CORE_CONF.server_id]
    )
    @discord.option(
        name="action",
        description="Select an action.",
        choices=["latest", "recent"]
    )
    async def earthquake(self, ctx: discord.ApplicationContext, action: str):
        await ctx.defer()
        earthquakes = self.quake_wrapper.get_earthquakes()
        if action == "latest":
            first_earthquake = earthquakes[0]
            await ctx.respond(
                embed=discord.Embed(
                    title=":earth_asia: Japan's Latest Earthquake",
                    description=f"""
                    **Date and Time:** {first_earthquake["issue_time"]}
                    **Location of Epicenter:** {first_earthquake["epicenter_location"]}
                    **Magnitude:** {first_earthquake["magnitude"]}
                    **Max Seismic Intensity:** {first_earthquake["max_seismic_intensity"]}
                    """
                )
            )
        elif action == "recent":
            earthquakes = earthquakes[:5]
            embed_fields = []
            for quake in earthquakes:
                embed_fields.append(
                    discord.EmbedField(
                        name=quake["issue_time"],
                        value=f"""
                        **Location of Epicenter:** {quake["epicenter_location"]}
                        **Magnitude:** {quake["magnitude"]}
                        **Max Seismic Intensity:** {quake["max_seismic_intensity"]}
                        """
                    )
                )
            await ctx.respond(
                embed=discord.Embed(
                    title=":earth_asia: Japan's Most Recent Earthquakes",
                    fields=embed_fields
                )
            )
        else:
            await ctx.respond("Not implemented.")

def setup(bot):
    bot.add_cog(EarthquakeCommands(bot))
