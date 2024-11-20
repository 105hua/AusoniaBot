# ----------------------------------------------------------#
# Licensed under the GNU Affero General Public License v3.0 #
# ----------------------------------------------------------#

# pylint: disable=E1101, R1702, R0911

import os
import asyncio
import aiohttp
import discord
from discord.ext import commands
from modules import configuration, logging_utils, database_utils, general_utils

CORE_CONF = configuration.CoreConfiguration()
DIFFUSION_CONF = configuration.DiffusionConfiguration()
LOGGER = logging_utils.Logger()

class DiffusionCommands(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.api_url = os.environ.get("ASYNC_API_URL", "http://127.0.0.1:8000")

    @commands.slash_command(
        name="generateimage",
        description="Generate an image with AI.",
        guild_ids=[CORE_CONF.server_id]
    )
    @discord.option(
        "image_type",
        description="The type of image you'd like to generate.",
        choices=DIFFUSION_CONF.get_diffusion_choices()
    )
    @discord.option(
        "width",
        description="The Width of the Image, in pixels. Maximum 1,280.",
        max_value=1280
    )
    @discord.option(
        "height",
        description="The Height of the Image, in pixels. Maximum 1,280.",
        max_value=1280
    )
    @discord.option(
        "prompt",
        description="The description of the image you'd like to generate."
    )
    @discord.option(
        "private",
        description="Choose whether you'd like other server members to see your image.",
        choices=["Yes", "No"]
    )
    @discord.option(
        "cfgscale",
        description="A number that indicates how closely you'd like the AI to follow your prompt.",
        choices=["Creative", "Balanced", "Precise"]
    )
    @discord.option(
        "steps",
        description="The number of iterations in the generation process. Max 30 steps.",
        max_value=50
    )
    @discord.option(
        "negative",
        description="Optionally, provide a negative prompt, which is what you would like to avoid in your image.",
        default=""
    )
    async def generateimage(
            self,
            ctx: discord.ApplicationContext,
            image_type: str,
            width: int,
            height: int,
            prompt: str,
            private: bool,
            cfgscale: str,
            steps: int,
            negative: str
    ):
        if not database_utils.is_allowed_diffusion(ctx.guild.id, ctx.author):
            invalid_permissions_embed = discord.Embed(
                title=":warning: Invalid Permissions",
                description="You do not have the correct permissions to use this command."
            )
            await ctx.respond(embed=invalid_permissions_embed)
            return
        option = DIFFUSION_CONF.get_option_by_name(image_type)
        if option is None:
            invalid_image_type_embed = discord.Embed(
                title=":warning: Invalid Image Type",
                description="The image type provided is invalid. Please try again."
            )
            await ctx.respond(embed=invalid_image_type_embed)
            return
        if option.is_nsfw:
            private = True
            if not ctx.channel.nsfw:
                invalid_image_type_embed = discord.Embed(
                    title=":warning: You cannot use an NSFW Model in a Non-NSFW Channel",
                    description="Models that have been marked as NSFW cannot be used in Non-NSFW Channels."
                )
                await ctx.respond(embed=invalid_image_type_embed, ephemeral=True)
                return
        async with aiohttp.ClientSession() as session:
            match cfgscale:
                case "Creative":
                    cfgscale = 4.0
                case "Balanced":
                    cfgscale = 7.5
                case "Precise":
                    cfgscale = 10.0
            async with session.post(
                self.api_url + "/inference",
                json={
                    "model": option.model_id,
                    "prompt": prompt,
                    "negative_prompt": negative,
                    "width": width,
                    "height": height,
                    "steps": steps,
                    "cfg_scale": cfgscale
                }
            ) as response:
                if not response.ok:
                    invalid_backend_response_embed = discord.Embed(
                        title=":warning: Could not reach the backend!",
                        description="The bot had a problem reaching the backend. Please try again later."
                    )
                    await ctx.respond(embed=invalid_backend_response_embed)
                    return
                data = await response.json()
                if data["success"]:
                    job_id = data["job_id"]
                    job_id_embed = discord.Embed(
                        title=":clock1: Pending",
                        description="Your image is currently in the queue to be generated. Please wait a few moments."
                    )
                    await ctx.respond(embed=job_id_embed, ephemeral=private)
                else:
                    invalid_backend_response_embed = discord.Embed(
                        title=":warning: Invalid Response from Backend!",
                        description="The bot received an invalid response from the backend. Please try again later."
                    )
                    await ctx.respond(embed=invalid_backend_response_embed)
                    return
            completed = False
            last_status = "PENDING"
            while not completed:
                async with session.get(
                    self.api_url + f"/get_result/{job_id}"
                ) as response:
                    if not response.ok:
                        invalid_backend_response_embed = discord.Embed(
                            title=":warning: Could not reach the backend!",
                            description="The bot had a problem reaching the backend. Please try again later."
                        )
                        await ctx.respond(embed=invalid_backend_response_embed)
                        return
                    data = await response.json()
                    if data["status"] == "PROCESSING" and last_status != "PROCESSING":
                        processing_embed = discord.Embed(
                            title=":clock1: Processing",
                            description="Your image is currently being generated. Please wait a few moments."
                        )
                        await ctx.edit(embed=processing_embed)
                    elif data["status"] == "COMPLETED":
                        completed = True
                        converted_image = general_utils.conver_data_url_to_bytes(data["image"])
                        elapsed_time = data["elapsed_time"]
                        image_embed = discord.Embed(
                            title=":white_check_mark: Completed!",
                            description="Your image has been successfully generated."
                        )
                        image_embed.set_image(url="attachment://image.png")
                        image_embed.set_footer(text=f"Time taken: {elapsed_time}")
                        await ctx.edit(embed=image_embed, file=discord.File(converted_image, "image.png", spoiler=private))
                        return
                    elif data["status"] == "FAILED":
                        failed_embed = discord.Embed(
                            title=":warning: Failed to Generate Image",
                            description=data["error"]
                        )
                        await ctx.edit(embed=failed_embed)
                        return
                    last_status = data["status"]
                    await asyncio.sleep(2)



def setup(bot):
    bot.add_cog(DiffusionCommands(bot))
