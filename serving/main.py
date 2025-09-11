import modal

app = modal.App("fableflux-gpt-oss-lora")

vllm_image = (
    modal.Image.from_registry("nvidia/cuda:12.8.1-devel-ubuntu22.04", add_python="3.12")
    .entrypoint([])
    .uv_pip_install(
        "vllm==0.10.1+gptoss",
        "huggingface_hub[hf_transfer]==0.34",
        pre=True,
        extra_options="--extra-index-url https://wheels.vllm.ai/gpt-oss/ "
                      "--extra-index-url https://download.pytorch.org/whl/nightly/cu128 "
                      "--index-strategy unsafe-best-match",
    )
)

MODEL_NAME   = "garethpaul/gpt-oss-20b-fableflux-mxfp4"   # <-- your new repo
MODEL_REV    = "main"
VLLM_PORT    = 8000
MINUTES      = 60
hf_cache     = modal.Volume.from_name("hf-cache", create_if_missing=True)
vllm_cache   = modal.Volume.from_name("vllm-cache", create_if_missing=True)

@app.function(
    image=vllm_image,
    gpu="H100:1",                     # or H200:1
    timeout=30 * MINUTES,
    volumes={"/root/.cache/huggingface": hf_cache, "/root/.cache/vllm": vllm_cache},
)
@modal.web_server(port=VLLM_PORT, startup_timeout=30 * MINUTES)
def serve():
    import subprocess
    cmd = [
        "vllm","serve", MODEL_NAME,
        "--revision", MODEL_REV,
        "--served-model-name", MODEL_NAME,
        "--host","0.0.0.0","--port", str(VLLM_PORT),
        "--max-model-len","8192",
        "--tensor-parallel-size","1",
        "--no-enforce-eager",
        "-O.cudagraph_capture_sizes=[1,2,4,8,16,32]"
    ]
    print("Launching:", " ".join(cmd))
    subprocess.Popen(" ".join(cmd), shell=True)

@app.local_entrypoint()
def url():
    print("Server URL:", serve.get_web_url())