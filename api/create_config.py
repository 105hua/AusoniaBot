"""
This script automatically generates a configuration file (config.json) for the Ausonia API by scanning
the models directory for .safetensors files. For each model found, it creates a configuration entry
containing:
- name: The model name (derived from the filename)
- pipeline: The model's pipeline type
- path: The absolute path to the model file
- is_nsfw: A flag indicating whether the model generates NSFW content (default: False)

The generated config.json is used by the API to load and manage available models. Keep in mind that
this script only assists in generating the config file, you will need to fill in the pipeline, the
is_nsfw flag and if you wish, the name.
"""

import json
import os

models_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")

if not os.path.exists(models_path):
    raise Exception("Can't find models folder!")

model_jsons = []

for model_file in os.listdir(models_path):
    if model_file.endswith(".safetensors"):
        model_json = {
            "id": model_file.replace(".safetensors", ""),
            "name": model_file.replace(".safetensors", ""),
            "pipeline": "PIPELINE_HERE",
            "path": f"./models/{model_file}",
            "is_nsfw": False
        }
        model_jsons.append(model_json)
        
with open("config.json", "w") as f:
    json.dump(model_jsons, f, indent=4)