# ----------------------------------------------------------#
# Licensed under the GNU Affero General Public License v3.0 #
# ----------------------------------------------------------#

import os
import uuid
from typing import Optional
import asyncio
from nudenet import NudeDetector
from modules import configuration, logging_utils
from modules.configuration import DiffusionOption

CORE_CONF = configuration.CoreConfiguration()
LOGGER = logging_utils.Logger()

DISALLOWED_LABELS = [
    "BUTTOCKS_EXPOSED",
    "FEMALE_BREAST_EXPOSED",
    "FEMALE_GENITALIA_EXPOSED",
    "MALE_BREAST_EXPOSED",
    "ANUS_EXPOSED",
    "FEET_EXPOSED",
    "FACE_MALE",
    "BELLY_EXPOSED",
    "MALE_GENITALIA_EXPOSED"
]

async def predict_nsfw(img_bytes: bytes) -> bool:
    detector = NudeDetector(model_path="./assets/640m.onnx")
    results = detector.detect(img_bytes)
    for detection in results:
        if detection["class"] in DISALLOWED_LABELS:
            if detection["score"] >= CORE_CONF.nsfw_threshold:
                return True
    return False
