# ----------------------------------------------------------#
# Licensed under the GNU Affero General Public License v3.0 #
# ----------------------------------------------------------#

from fastapi import FastAPI
from modules.request_models import InferenceRequest
from modules import general
from modules.job_processing import DiffusionJobProcessor

APP = FastAPI()
CONFIG = general.get_config()
NEGATIVE_PROMPT = general.get_negative_prompt()
JOB_PROCESSOR = DiffusionJobProcessor()

@APP.on_event("startup")
def startup():
    JOB_PROCESSOR.start_processing()

@APP.on_event("shutdown")
def shutdown():
    JOB_PROCESSOR.stop_processing()

@APP.get("/")
def read_root():
    return {
        "text": "We're online!"
    }

@APP.get("/queue_info")
def read_queue():
    return {
        "Hello": "World"
    }

@APP.get("/get_negative_prompt")
def get_negative_prompt():
    return {
        "negative_prompt": NEGATIVE_PROMPT
    }

@APP.get("/get_models")
def get_models():
    models = []
    for model in CONFIG:
        models.append({
            "id": model["id"],
            "name": model["name"],
            "is_nsfw": model["is_nsfw"]
        })
    return {
        "models": models
    }

@APP.post("/inference")
def inference(inference_req: InferenceRequest):
    job_id = JOB_PROCESSOR.add_job(inference_req.dict())
    return {
        "success": True,
        "job_id": job_id
    }

@APP.get("/get_result/{job_id}")
def get_result(job_id: str):
    result = JOB_PROCESSOR.get_result(job_id)
    return result
