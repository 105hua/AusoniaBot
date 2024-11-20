# ----------------------------------------------------------#
# Licensed under the GNU Affero General Public License v3.0 #
# ----------------------------------------------------------#

# pylint: disable=E1101

import random
import aiohttp
from jokeapi import Jokes
import discord
from discord.ext import commands
from modules import configuration

CORE_CONF = configuration.CoreConfiguration()
EIGHT_BALL_RESPONSES = [
    "It is certain.",
    "It is decidedly so.",
    "Without a doubt.",
    "Yes, definitely.",
    "You may rely on it.",
    "As I see it, yes.",
    "Most likely.",
    "Outlook is good.",
    "Yes.",
    "Signs point to yes.",
    "Reply hazy, try again.",
    "Ask again later.",
    "Better not tell you now.",
    "Cannot predict now.",
    "Concentrate and ask again.",
    "Don't count on it.",
    "My reply is no.",
    "My sources say no.",
    "Outlook not so good.",
    "Very doubtful."
]

class FunCommands(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.slash_command(
        name="joke",
        description="Get a random joke!",
        guild_ids=[CORE_CONF.server_id]
    )
    async def joke(self, ctx: discord.ApplicationContext):
        joke_api = await Jokes()
        joke = await joke_api.get_joke(
            joke_type="single",
            blacklist=[
                "nsfw",
                "religious",
                "political",
                "racist",
                "sexist"
            ]
        )
        joke_embed = discord.Embed(
            title=":joy: Here's your joke!",
            description=joke["joke"]
        )
        await ctx.respond(embed=joke_embed)

    @commands.slash_command(
        name="rolldice",
        description="Roll a virtual dice!",
        guild_ids=[CORE_CONF.server_id]
    )
    async def rolldice(self, ctx: discord.ApplicationContext):
        await ctx.respond(
            embed=discord.Embed(
                title=":game_die: Dice Roll",
                description=f"You've rolled a `{random.randint(1, 6)}`"
            )
        )

    @commands.slash_command(
        name="eightball",
        description="Ask the Magic 8 Ball a Question.",
        guild_ids=[CORE_CONF.server_id]
    )
    @discord.option(
        name="question",
        description="The question you'd like to ask. Maximum 100 characters including spaces.",
        type=discord.SlashCommandOptionType.string
    )
    async def eightball(self, ctx: discord.ApplicationContext, question: str):
        if len(question) > 100:
            question_too_long_embed = discord.Embed(
                title=":warning: Your question is too long!",
                description="Please make your question shorter and try again."
            )
            await ctx.respond(embed=question_too_long_embed)
            return
        response = EIGHT_BALL_RESPONSES[random.randint(0, len(EIGHT_BALL_RESPONSES))]
        response_embed = discord.Embed(
            title=question,
            description=response
        )
        await ctx.respond(embed=response_embed)

    @commands.slash_command(
        name="flipcoin",
        description="Flip a coin!",
        guild_ids=[CORE_CONF.server_id]
    )
    async def flipcoin(self, ctx: discord.ApplicationContext):
        flip_coin_embed = discord.Embed(
            title=":coin: Flip Coin",
            description=f"You've flipped {'Heads' if random.randint(0, 1) == 1 else 'Tails'}"
        )
        await ctx.respond(embed=flip_coin_embed)

    @commands.slash_command(
        name="meme",
        description="Get a random meme!",
        guild_ids=[CORE_CONF.server_id]
    )
    @discord.option(
        name="subreddit",
        description="An optional subreddit to get a meme from.",
        type=discord.SlashCommandOptionType.string,
        required=False
    )
    async def meme(self, ctx: discord.ApplicationContext, subreddit: str = ""):
        await ctx.defer()
        async with aiohttp.ClientSession() as session:
            while True:
                async with session.get(
                        "https://meme-api.com/gimme/" + subreddit
                ) as response:
                    if not response.ok:
                        invalid_response_embed = discord.Embed(
                            title=":warning: Something went wrong",
                            description="The bot could not get a meme for you at this time. This is usually due to "
                                        "the subreddit specified either having no posts or not existing."
                        )
                        await ctx.respond(embed=invalid_response_embed)
                        return
                    data = await response.json()
                    if not data["nsfw"]:
                        image_url = data["url"]
                        title = data["title"]
                        author = data["author"]
                        subreddit = data["subreddit"]
                        meme_embed = discord.Embed(
                            title=title,
                            description=f"Posted by `{author}` on the `{subreddit}` subreddit.",
                            image=image_url
                        )
                        await ctx.respond(embed=meme_embed)
                        break


def setup(bot):
    bot.add_cog(FunCommands(bot))
