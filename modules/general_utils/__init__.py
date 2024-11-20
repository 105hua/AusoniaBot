# ----------------------------------------------------------#
# Licensed under the GNU Affero General Public License v3.0 #
# ----------------------------------------------------------#

"""The General Utilities for the bot."""
import os
import base64
import io
import aiohttp
from modules.configuration import CoreConfiguration

CORE_CONFIG = CoreConfiguration()

def conver_data_url_to_bytes(data_url: str) -> io.BytesIO:
    return io.BytesIO(base64.b64decode(data_url.split(",")[1]))

async def check_status() -> bool:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(CORE_CONFIG.swarm_url) as response:
                return response.status == 200
        except aiohttp.ClientConnectorError:
            return False

def are_diffusion_commands_enabled():
    return os.path.exists(os.path.join(os.getcwd(), ".NO_DIFFUSION")) is not True
