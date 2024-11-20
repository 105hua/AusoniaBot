# ----------------------------------------------------------#
# Licensed under the GNU Affero General Public License v3.0 #
# ----------------------------------------------------------#

import json

def get_negative_prompt():
    with open("negative_prompt.txt", "r", encoding="UTF-8") as f:
        lines = f.readlines()
        negative_prompt = ", ".join(line.strip() for line in lines)
    return negative_prompt

def get_config():
    with open("config.json", "r", encoding="UTF-8") as f:
        config = json.load(f)
    return config
