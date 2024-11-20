# ----------------------------------------------------------#
# Licensed under the GNU Affero General Public License v3.0 #
# ----------------------------------------------------------#

import os
import json
import typing
import http.client

class CoreConfiguration:
    def __init__(self):
        with open(os.path.join(os.getcwd(), "config", "core.json"), encoding="UTF-8") as f:
            core_config = json.loads(f.read())
        self.bot_token = core_config["bot_token"]
        self.server_id = core_config["server_id"]
        self.owner_id = core_config["owner_id"]
        self.nsfw_threshold = core_config["nsfw_threshold"]


class DiffusionOption:
    def __init__(self, model_id: str, name: str, is_nsfw: bool):
        self.model_id = model_id
        self.name = name
        self.is_nsfw = is_nsfw

class DiffusionConfiguration:
    def __init__(self):
        api_url = os.environ.get("SYNC_API_URL", "http://127.0.0.1:8000")
        conn = http.client.HTTPConnection(api_url)
        conn.request("GET", "/get_models")
        response = conn.getresponse()
        if response.status != 200:
            raise ValueError("Could not get models from API")
        data = json.loads(response.read())
        options = []
        for option in data["models"]:
            options.append(
                DiffusionOption(
                    option["id"],
                    option["name"],
                    option["is_nsfw"]
                )
            )
        self.diffusion_options = options


    def get_diffusion_choices(self) -> list[str]:
        choices = []
        for option in self.diffusion_options:
            choices.append(option.name)
        return choices

    def get_option_by_name(self, option_name: str) -> typing.Optional[DiffusionOption]:
        for option in self.diffusion_options:
            if option.name == option_name:
                return option
        return None
