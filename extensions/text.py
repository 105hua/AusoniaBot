# ----------------------------------------------------------#
# Licensed under the GNU Affero General Public License v3.0 #
# ----------------------------------------------------------#

# pylint: disable=E1101

import discord
from discord.ext import commands
from fancify_text import fancify
from modules import configuration

CORE_CONF = configuration.CoreConfiguration()
FONT_DICT = {
    "Bold": "bold",
    "Italic": "italic",
    "Bold Italic": "boldItalic",
    "Monospaced": "monospaced",
    "Wide": "wide",
    "Double Struck": "doubleStruck",
    "Script": "script",
    "Fraktur": "fraktur",
    "Bold Fraktur": "boldFraktur",
    "Squared": "squared",
    "Circled": "circled"
}

class TextCommands(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.slash_command(
        name="fancytext",
        description="Convert some text to bold.",
        guild_ids=[CORE_CONF.server_id]
    )
    @discord.option(
        name="input_text",
        description="The text you'd like to convert."
    )
    @discord.option(
        name="style",
        description="The style you'd like to convert to.",
        choices=FONT_DICT.keys()
    )
    async def fancytext(self, ctx: discord.ApplicationContext, input_text: str, style: str):
        fancified_text = fancify(
            inputText=input_text,
            style=FONT_DICT[style]
        )
        fancified_embed = discord.Embed(
            title="Fancified Text",
            description=fancified_text
        )
        await ctx.respond(embed=fancified_embed)

def setup(bot):
    bot.add_cog(TextCommands(bot))
