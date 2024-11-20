# ----------------------------------------------------------#
# Licensed under the GNU Affero General Public License v3.0 #
# ----------------------------------------------------------#

import threading
import queue
import uuid
import base64
import gc
import io
import os
import time
from typing import Optional
import diffusers
import torch
from DeepCache import DeepCacheSDHelper
from modules import general

class DiffusionResult:
    def __init__(self, job_id, result):
        self.job_id = job_id
        self.result = result

class DiffusionJobProcessor:
    def __init__(self):
        self._job_queue = queue.Queue()
        self._thread = threading.Thread(target=self._process_jobs)
        self._stop_event = threading.Event()
        self._thread.daemon = True
        self._results_map = {}
        self._config = general.get_config()
        self._auth_token = os.environ.get("AUTH_TOKEN", None)

    def start_processing(self):
        self._thread.start()

    def stop_processing(self):
        self._stop_event.set()
        self._thread.join()

    def _get_model_from_config(self, model_id: str) -> Optional[dict]:
        """
        Looks up a model configuration in the internal configuration list
        by its ID.

        Args:
            model_id: The ID of the model to look up.

        Returns:
            A dictionary representing the model configuration if found,
            otherwise None.
        """
        for model in self._config:
            if model["id"] == model_id:
                return model
        return None

    def add_job(self, job_data) -> str:
        """
        Adds a new job to the queue with the given data. Returns a unique job
        ID which can be used to retrieve the job result.

        Args:
            job_data: A dictionary containing the model ID, prompt, negative
                prompt, width, height, steps, and guidance scale for the job.

        Returns:
            A unique job ID which can be used to retrieve the job result.
        """
        generated_uuid = str(uuid.uuid4())
        while generated_uuid in self._results_map:
            generated_uuid = str(uuid.uuid4())
        self._job_queue.put({
            "id": generated_uuid,
            "data": job_data
        })
        self._results_map[generated_uuid] = {
            "status": "PENDING"
        }
        return generated_uuid

    def get_result(self, job_id: str) -> dict:
        """
        Retrieves the result of a job with the given ID. If the job ID does not exist,
        an empty dictionary is returned.

        Args:
            job_id: The unique ID of the job to retrieve the result for.

        Returns:
            A dictionary containing the result of the job. The dictionary may contain
            a "status" key with a value of "SUCCESS" or "ERROR". If the job completed
            successfully, the dictionary will contain an "image" key with the base64
            encoded image and an "elapsed" key with the time it took to process the
            job in seconds. If the job failed, the dictionary will contain an "error"
            key with an error message.
        """
        return self._results_map.get(job_id, {})

    def _process_jobs(self):
        """
        Continuously processes jobs from the job queue until a stop event is set.
        
        Each job contains data to perform inference using a specified model pipeline from 
        the configuration. Results, including success status and the encoded image, are 
        stored in the results map. If the pipeline for a model cannot be found, an error 
        message is recorded.

        The function retrieves jobs from the queue, loads the appropriate model pipeline,
        and generates an image based on the job's parameters. The image is then encoded 
        in base64 format and stored in the results map along with the processing time.
        """
        while not self._stop_event.is_set():
            # pylint: disable=W0718
            try:
                job = self._job_queue.get(block=True, timeout=1)
                try:
                    diffusers.utils.logging.set_verbosity_error()
                    diffusers.utils.logging.enable_default_handler()
                    diffusers.utils.logging.enable_explicit_format()
                    job_data = job["data"]
                    model = self._get_model_from_config(job_data["model"])
                    if not hasattr(diffusers, model["pipeline"]):
                        self._results_map[job["id"]] = {
                            "status": "FAILED",
                            "error": f"Pipeline '{model['pipeline']}' not found"
                        }
                        self._job_queue.task_done()
                        continue
                    self._results_map[job["id"]] = {
                        "status": "PROCESSING"
                    }
                    pipe_class = getattr(diffusers, model["pipeline"])
                    if self._auth_token is not None:
                        pipe = pipe_class.from_single_file(
                            model["path"],
                            torch_dtype=torch.float16,
                            token=self._auth_token,
                            use_safetensors=True
                        )
                    else:
                        pipe = pipe_class.from_single_file(
                            model["path"],
                            torch_dtype=torch.float16,
                            use_safetensors=True
                        )
                    pipe.enable_model_cpu_offload()
                    tokenizer = pipe.tokenizer
                    prompt_tokens = tokenizer(
                        job_data["prompt"],
                        return_tensors="pt"
                    )
                    negative_prompt_tokens = tokenizer(
                        job_data["negative_prompt"],
                        return_tensors="pt"
                    )
                    num_prompt_tokens = len(prompt_tokens["input_ids"][0])
                    num_negative_prompt_tokens = len(negative_prompt_tokens["input_ids"][0])
                    del prompt_tokens
                    del negative_prompt_tokens
                    del tokenizer
                    helper = DeepCacheSDHelper(
                        pipe=pipe
                    )
                    helper.set_params(
                        cache_interval=3,
                        cache_branch_id=0
                    )
                    helper.enable()
                    if num_prompt_tokens > 75:
                        self._results_map[job["id"]] = {
                            "status": "FAILED",
                            "error": "Prompt is too long"
                        }
                        continue
                    if num_negative_prompt_tokens > 75:
                        self._results_map[job["id"]] = {
                            "status": "FAILED",
                            "error": "Negative Prompt is too long"
                        }
                        continue
                    start_time = time.time()
                    image = pipe(
                        job_data["prompt"],
                        negative_prompt=job_data["negative_prompt"] if job_data["negative_prompt"] != "" else None,
                        width=job_data["width"],
                        height=job_data["height"],
                        num_inference_steps=job_data["steps"],
                        guidance_scale=job_data["cfg_scale"]
                    ).images[0]
                    end_time = time.time()
                    elapsed_time = f"{(end_time - start_time):.2f}s"
                    image_stream = io.BytesIO()
                    image.save(image_stream, format="PNG")
                    encoded_image = base64.b64encode(image_stream.getvalue()).decode("UTF-8")
                    encoded_image = f"data:image/png;base64,{encoded_image}"
                    self._results_map[job["id"]] = {
                        "status": "COMPLETED",
                        "image": encoded_image,
                        "elapsed_time": elapsed_time
                    }
                except Exception as e:
                    self._results_map[job["id"]] = {
                        "status": "FAILED",
                        "error": "An exception was thrown."
                    }
                    print(e)
                finally:
                    if "pipe" in locals() or "pipe" in globals():
                        del pipe
                    if "helper" in locals() or "helper" in globals():
                        del helper
                    torch.cuda.empty_cache()
                    gc.collect()
                    self._job_queue.task_done()
            except queue.Empty:
                pass
