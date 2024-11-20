# ----------------------------------------------------------#
# Licensed under the GNU Affero General Public License v3.0 #
# ----------------------------------------------------------#

import os
from datetime import datetime
import discord
import aiofiles
from modules import (configuration,
                     logging_utils,
                     database_utils)

CORE_CONF = configuration.CoreConfiguration()
BOT = discord.Bot()
LOGGER = logging_utils.Logger()

@BOT.event
async def on_ready():
    #
    # Create generated images dir.
    #
    os.makedirs(os.path.join(os.getcwd(), "generated_images"), exist_ok=True)
    #
    # Setup Database
    #
    LOGGER.info("Setting up database...")
    if database_utils.setup_database():
        LOGGER.info("Setup Success!")
    else:
        LOGGER.warn("Setup failed, things might go badly!")
    #
    # Write the current time to disk for the uptime command.
    #
    async with aiofiles.open("start_time.txt", "w", encoding="UTF-8") as f:
        await f.write(str(int(datetime.now().timestamp())))
    #
    # Log bot ready
    #
    LOGGER.info("Bot is now ready!")

for extension in os.listdir(os.path.join(os.getcwd(), "extensions")):
    if not extension.startswith("_") and extension.endswith(".py"):
        BOT.load_extension(f"extensions.{extension[:-3]}")
        LOGGER.info(f"Loaded the '{extension[:-3]}' extension!")

BOT.run(CORE_CONF.bot_token)
