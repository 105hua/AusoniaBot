# ----------------------------------------------------------#
# Licensed under the GNU Affero General Public License v3.0 #
# ----------------------------------------------------------#

from pydantic import BaseModel

class InferenceRequest(BaseModel):
    model: str
    prompt: str
    negative_prompt: str
    width: int
    height: int
    steps: int
    cfg_scale: float
