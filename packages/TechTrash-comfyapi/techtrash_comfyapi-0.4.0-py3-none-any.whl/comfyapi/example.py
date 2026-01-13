from main import ComfyAPI
import json
import asyncio

with open("fluxdev.json", "r") as f:
    fluxdev = json.load(f)

comfy = ComfyAPI(
    api_key="",
    s3_endpoint="https://s3.gra.io.cloud.ovh.net",
    s3_bucket="s3-nextprotocol",
    s3_region="gra",
    s3_key_id="ebbe6df1abe7432496a033c81d744cee",
    s3_secret="bd0cec0afb104eda966f94f1f0cd48db",
    absolute_paths_comfyui=["/app/comfyui/0"],
    models_path="/app/models",
    ports=[3050]
)


models_input = [
    {
        "name": "flux1-dev.safetensors",
        "type": "unet"
    },
    {
        "name": "clip_l.safetensors",
        "type": "clip"
    },
    {
        "name": "t5xxl_fp16.safetensors",
        "type": "clip"
    },
    {
        "name": "ae.safetensors",
        "type": "vae"
    }
]

loras_input = []


settings_scaled_by_gpu_count = [
    {
        "title": "API - BATCH SIZE",
        "value": 1
    }
]

settings_fixed_per_gpu = [
    {
        "title": "API - UNET NAME",
        "value": "flux1-dev.safetensors"
    },
    {
        "title": "API - CLIP 1",
        "value": "clip_l.safetensors"
    },
    {
        "title": "API - CLIP 2",
        "value": "t5xxl_fp16.safetensors"
    },
    {
        "title": "API - VAE",
        "value": "ae.safetensors"
    },
    {
        "title": "API - PROMPT",
        "value": "A beautiful woman with long blonde hair and blue eyes"
    },
    {
        "title": "API - STEP",
        "value": 20
    }
]
    
async def main() -> list[str]:
    paths: list[str] = await comfy.execute_workflow_TtI( # type: ignore 
        workflow_json=fluxdev,
        models=models_input,
        loras=loras_input, # type: ignore
        settings_scaled_by_gpu_count=settings_scaled_by_gpu_count,
        settings_fixed_per_gpu=settings_fixed_per_gpu
        )

    return paths # type: ignore

if __name__ == "__main__":
    paths = asyncio.run(main())
    print(paths)
    for i, path in enumerate(paths): # type: ignore
        print(f"Image {i+1} saved to {path}")