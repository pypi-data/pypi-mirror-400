import os
import subprocess
from s3file import OvhS3 # type: ignore
import pynvml # type: ignore
from typing import Literal, Any
import requests
import math
import asyncio
import pprint
import random

GPU = Literal[
    "RTX 4090", "RTX 5090", "RTX 6000 Ada", "A40", "H100", "A100", "B200", "H200", "Unknown GPU"
]

class GPUMonitor:
    def __init__(self):
        pynvml.nvmlInit()
        self.gpu_count = pynvml.nvmlDeviceGetCount()
        self.gpu_name = self.get_gpu_name()
        pynvml.nvmlShutdown()

    def get_gpu_name(self) -> GPU:
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)  # type: ignore
        name = pynvml.nvmlDeviceGetName(handle)  # type: ignore
        if isinstance(name, bytes):
            name = name.decode("utf-8")

        match name:
            case _ if "4090" in name:
                return "RTX 4090"
            case _ if "5090" in name:
                return "RTX 5090"
            case _ if "6000 Ada" in name:
                return "RTX 6000 Ada"
            case _ if "A40" in name:
                return "A40"
            case _ if "H100" in name:
                return "H100"
            case _ if "A100" in name:
                return "A100"
            case _ if "B200" in name:
                return "B200"
            case _ if "H200" in name:
                return "H200"
            case _:
                return "Unknown GPU"


class ComfyAPI(GPUMonitor):
    def __init__(self,  api_key: str, 
                        s3_endpoint: str, s3_bucket: str, s3_region: str, s3_key_id: str, s3_secret: str,
                        absolute_paths_comfyui: list[str], models_path: str, ports: list[int]):
        '''
        Initialize the ComfyAPI instance with all required configuration parameters.
        
        Args:
            api_key: The API key used for authentication with the ComfyUI instances.
            s3_endpoint: The S3 endpoint URL for OVH object storage (e.g., 'https://s3.gra.io.cloud.ovh.net').
            s3_bucket: The name of the S3 bucket where files will be stored.
            s3_region: The AWS region where the S3 bucket is located (e.g., 'gra').
            s3_key_id: The S3 access key ID for authentication.
            s3_secret: The S3 secret access key for authentication.
            paths_comfyui: List of file system paths to the ComfyUI installation directories. (e.g. ['/home/user/0/comfyui', '/home/user/1/comfyui'])
            ports: List of port numbers corresponding to each ComfyUI instance. (e.g. [3050, 3051])
        
        Note:
            The paths_comfyui and ports lists must have the same length, as each path
            corresponds to a port at the same index position.
        '''
        super().__init__()

        self.api_key = api_key
        self.s3 = OvhS3(
            endpoint=s3_endpoint,
            bucket=s3_bucket,
            region=s3_region,
            key_id=s3_key_id,
            secret=s3_secret
        )

        if len(absolute_paths_comfyui) != len(ports):
            raise ValueError("The absolute_paths_comfyui and ports lists must have the same length")

        self.absolute_paths_comfyui = absolute_paths_comfyui
        self.ports = ports
        self.models_path = models_path

        self.sessions_comfyui: list[dict[str, Any]] = self.initialize()

    def initialize(self) -> list[dict[str, Any]]:
        env = os.environ.copy()
        sessions_comfyui: list[dict[str, Any]] = []

        print("--------------------------------")
        print("Initialize ComfyUI instances")
        print(f"Number of GPU : {self.gpu_count}")
        print(f"GPU name : {self.gpu_name}")
        print("--------------------------------")

        for i in range(self.gpu_count):
            env["CUDA_VISIBLE_DEVICES"] = str(i)
            port = self.ports[i]
            path = self.absolute_paths_comfyui[i]
            subprocess.Popen(
                [
                    "python",
                    "main.py",
                    "--listen",
                    "0.0.0.0",
                    "--port",
                    str(port),
                    "--disable-auto-launch",
                    "--disable-metadata",
                    "--output-directory",
                    f"{path}/output",
                    "--temp-directory",
                    f"{path}/temp",
                ],
                env=env,
                cwd=path,
            )
            print(f"ComfyUI instance {i} initialized on port {port}")
            sessions_comfyui.append({
                "port": port,
                "path": path
            })
        
        print("--------------------------------")
        print("ComfyUI instances initialized")
        print("--------------------------------")

        return sessions_comfyui

    def download_file_from_url(self, url: str, path: str) -> None:
        '''
        Download a file from a URL to a local path.
        '''
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError(f"Failed to download file from {url}")
        with open(path, "wb") as f:
            f.write(response.content)
        print(f"File {path} downloaded from {url}")
        return None

    def check_models(self, models: list[dict[str, Any]]) -> bool:
        '''
        Check if the models are available in the models path.
        '''
        for model in models:
            path_model = os.path.join(self.models_path, model["type"], model["name"])
            if not os.path.exists(path_model):
                raise ValueError(f"Model {model['name']} not found in the models path")

        return True

    def check_and_download_loras(self, loras: list[dict[str, Any]]) -> None:
        '''
        Check if the loras are available in the models path.
        '''
        path_loras = os.path.join(self.models_path, "loras")
        if not os.path.exists(path_loras):
            os.makedirs(path_loras)

        for lora in loras:
            path_lora = os.path.join(path_loras, lora["name"])
            if not os.path.exists(path_lora):
                self.download_file_from_url(lora["url"], path_lora)
        return None

    def _add_picture_to_comfyui(self, url_picture: str) -> str:
        picture_name = url_picture.split("/")[-1]
        
        for abs_path_comfyui in self.absolute_paths_comfyui:
            path_folder_picture = os.path.join(abs_path_comfyui, "input")
            picture_path = os.path.join(path_folder_picture, picture_name)
            if not os.path.exists(picture_path):
                self.download_file_from_url(url_picture, picture_path)
            
        return picture_name
            

    def prepare_workflow(self, workflow_json: dict[str, Any], settings_scaled_by_gpu_count: list[dict[str, Any]], settings_fixed_per_gpu: list[dict[str, Any]], loras: list[dict[str, Any]]) -> dict[str, Any]:
        final_workflow: dict[str, Any] = workflow_json.copy()

        for _, value in final_workflow.items():
            meta_title = value["_meta"]["title"]

            for setting in settings_scaled_by_gpu_count:
                if setting["title"] == meta_title:
                    new_value = math.ceil(setting["value"] / self.gpu_count)
                    value["inputs"]["value"] = new_value
                    break

            for setting in settings_fixed_per_gpu:
                if setting["title"] == meta_title:

                    if setting["title"].startswith("API - PICTURE"):
                        picture_name = self._add_picture_to_comfyui(setting["value"])
                        value["inputs"]["image"] = picture_name
                    else:
                        value["inputs"]["value"] = setting["value"]
                    break

            if value["class_type"] == "Power Lora Loader (rgthree)":
                for i, lora in enumerate(loras):
                    value["inputs"][f"lora_{i+1}"] = {
                        "on": True,
                        "lora": lora["name"],
                        "strength": lora["strength"]
                    }

        print("------------- FINAL WORKFLOW -------------")
        pprint.pprint(final_workflow)
        print("-----------------------------------------")
        return final_workflow

    async def comfyui_is_ready(self, comfyui_url_api: str) -> None:
        while True:
            try:
                response = await asyncio.to_thread(requests.get, f"{comfyui_url_api}/history")
                if response.status_code == 200:
                    print(f"ComfyUI is ready : {comfyui_url_api}")
                    break
            except Exception:
                print(f"Error checking if ComfyUI is ready, retrying in 0.5 seconds")
                await asyncio.sleep(0.5)
        return None

    async def send_workflow_to_comfyui_and_wait_for_images(self, workflow_json: dict[str, Any], comfyui_url_api: str, path_to_save_images: str, random_seed: int) -> list[str]:
        await self.comfyui_is_ready(comfyui_url_api)

        # Add random seed to workflow json
        for _, value in workflow_json.items():
            title = value["_meta"]["title"]
            if title == "K - SEED":
                
                print("-----------  RANDOM SEED FOUND ------------------")
                print(f"Adding random seed to workflow json : {random_seed}")
                print("-------------------------------------------------")

                value["inputs"]["value"] = random_seed
                break
        
        add_queue_comfy = await asyncio.to_thread(requests.post, f"{comfyui_url_api}/prompt", json={"prompt": workflow_json})
        if add_queue_comfy.status_code != 200:
            raise ValueError(f"Failed to add workflow to ComfyUI: {add_queue_comfy.text}")

        queue_id = add_queue_comfy.json()["prompt_id"]

        while True:
            print(f"Waiting for workflow to be processed : {queue_id}")
            history_request = await asyncio.to_thread(requests.get, f"{comfyui_url_api}/history/{queue_id}")
            history_response = history_request.json()

            if history_response != {} and history_response[queue_id]["status"]["status_str"] == "success":
                history_outputs = history_response[queue_id]["outputs"]
                break
            await asyncio.sleep(2)

        print(f"Workflow processed : {queue_id}")
        outputs_path_images: list[str] = []
        print(f"History outputs :")
        print(history_outputs)
        for _, value in history_outputs.items():
            for image in value.get("images", []):
                if image["type"] == "output":
                    outputs_path_images.append(os.path.join(path_to_save_images, image["filename"]))
        print(f"Outputs path images : {outputs_path_images}")
        return outputs_path_images

    async def execute_workflow_TtI(self, workflow_json: dict[str, Any], models: list[dict[str, Any]], loras: list[dict[str, Any]] , settings_scaled_by_gpu_count: list[dict[str, Any]], settings_fixed_per_gpu: list[dict[str, Any]]) -> list[str]:
        '''
        Execute a workflow on the ComfyUI instances.

        Args:
            workflow_json: The JSON workflow to execute.
            models: List of models to use in the workflow.
            loras: List of loras to use in the workflow.
            settings_scaled_by_gpu_count: Settings that are divided by the number of GPUs.
                                         Each GPU will receive the total value divided by GPU count.
                                         Example: batch_size=4 with 4 GPUs -> each GPU gets batch_size=1.
            settings_fixed_per_gpu: Settings that remain unchanged per GPU.
                                   Each GPU will receive the same value regardless of GPU count.
                                   Example: steps=20 with 4 GPUs -> each GPU runs 20 steps.
        '''
        if not self.check_models(models):
            raise ValueError("Models not found in the models path")

        self.check_and_download_loras(loras)

        final_workflow_json = self.prepare_workflow(workflow_json, settings_scaled_by_gpu_count, settings_fixed_per_gpu, loras)

        generate_images_corontine = await asyncio.gather(
            *[self.send_workflow_to_comfyui_and_wait_for_images(
                final_workflow_json, 
                f"http://localhost:{session['port']}", 
                os.path.join(session["path"], "output"),
                random.randint(0, 999998)
            ) for session in self.sessions_comfyui]
        )

        full_output_images: list[str] = []
        for images in generate_images_corontine:
            full_output_images.extend(images)

        return full_output_images