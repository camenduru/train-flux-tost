FROM runpod/pytorch:2.2.1-py3.10-cuda12.1.1-devel-ubuntu22.04
WORKDIR /content
ENV PATH="/home/camenduru/.local/bin:${PATH}"

RUN adduser --disabled-password --gecos '' camenduru && \
    adduser camenduru sudo && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers && \
    chown -R camenduru:camenduru /content && \
    chmod -R 777 /content && \
    chown -R camenduru:camenduru /home && \
    chmod -R 777 /home && \
    apt update -y && add-apt-repository -y ppa:git-core/ppa && apt update -y && apt install -y aria2 git git-lfs unzip ffmpeg

USER camenduru

RUN pip install -q torch==2.4.0+cu121 torchvision==0.19.0+cu121 torchaudio==2.4.0+cu121 torchtext==0.18.0 torchdata==0.8.0 --extra-index-url https://download.pytorch.org/whl/cu121 \
    transformers==4.44.2 diffusers==0.30.1 accelerate==0.33.0 peft==0.12.0 controlnet_aux==0.0.9 opencv-python==4.10.0.84 python-slugify==8.0.4 oyaml==1.0 albumentations==1.4.14 \
    lpips==0.1.4 einops==0.8.0 sentencepiece==0.2.0 huggingface_hub==0.24.6 hf_transfer==0.1.8 lycoris-lora==3.0.0.post1 flatten_json==0.1.14 pyyaml==6.0.2 tensorboard==2.17.1 \
    kornia==0.7.3 invisible-watermark==0.2.0 toml==0.10.2 pydantic==2.8.2 omegaconf==2.3.0 k-diffusion==0.1.1.post1 open_clip_torch==2.26.1 timm==0.6.7 prodigyopt==1.0 python-dotenv==1.0.1 \
    bitsandbytes==0.43.3 pytorch_fid==0.3.0 optimum-quanto==0.2.4 protobuf==5.28.0 runpod && \
    git clone https://github.com/ostris/ai-toolkit /content/ai-toolkit && cd /content/ai-toolkit && git submodule update --init --recursive && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/FLUX.1-dev-diffusers/raw/main/scheduler/scheduler_config.json -d /content/model/scheduler -o scheduler_config.json && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/FLUX.1-dev-diffusers/raw/main/text_encoder/config.json -d /content/model/text_encoder -o config.json && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/FLUX.1-dev-diffusers/resolve/main/text_encoder/model.safetensors -d /content/model/text_encoder -o model.safetensors && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/FLUX.1-dev-diffusers/raw/main/text_encoder_2/config.json -d /content/model/text_encoder_2 -o config.json && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/FLUX.1-dev-diffusers/resolve/main/text_encoder_2/model-00001-of-00002.safetensors -d /content/model/text_encoder_2 -o model-00001-of-00002.safetensors && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/FLUX.1-dev-diffusers/resolve/main/text_encoder_2/model-00002-of-00002.safetensors -d /content/model/text_encoder_2 -o model-00002-of-00002.safetensors && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/FLUX.1-dev-diffusers/raw/main/text_encoder_2/model.safetensors.index.json -d /content/model/text_encoder_2 -o model.safetensors.index.json && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/FLUX.1-dev-diffusers/raw/main/tokenizer/merges.txt -d /content/model/tokenizer -o merges.txt && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/FLUX.1-dev-diffusers/raw/main/tokenizer/special_tokens_map.json -d /content/model/tokenizer -o special_tokens_map.json && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/FLUX.1-dev-diffusers/raw/main/tokenizer/tokenizer_config.json -d /content/model/tokenizer -o tokenizer_config.json && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/FLUX.1-dev-diffusers/raw/main/tokenizer/vocab.json -d /content/model/tokenizer -o vocab.json && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/FLUX.1-dev-diffusers/raw/main/tokenizer_2/special_tokens_map.json -d /content/model/tokenizer_2 -o special_tokens_map.json && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/FLUX.1-dev-diffusers/resolve/main/tokenizer_2/spiece.model -d /content/model/tokenizer_2 -o spiece.model && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/FLUX.1-dev-diffusers/raw/main/tokenizer_2/tokenizer.json -d /content/model/tokenizer_2 -o tokenizer.json && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/FLUX.1-dev-diffusers/raw/main/tokenizer_2/tokenizer_config.json -d /content/model/tokenizer_2 -o tokenizer_config.json && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/FLUX.1-dev-diffusers/raw/main/transformer/config.json -d /content/model/transformer -o config.json && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/FLUX.1-dev-diffusers/resolve/main/transformer/diffusion_pytorch_model-00001-of-00003.safetensors -d /content/model/transformer -o diffusion_pytorch_model-00001-of-00003.safetensors && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/FLUX.1-dev-diffusers/resolve/main/transformer/diffusion_pytorch_model-00002-of-00003.safetensors -d /content/model/transformer -o diffusion_pytorch_model-00002-of-00003.safetensors && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/FLUX.1-dev-diffusers/resolve/main/transformer/diffusion_pytorch_model-00003-of-00003.safetensors -d /content/model/transformer -o diffusion_pytorch_model-00003-of-00003.safetensors && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/FLUX.1-dev-diffusers/raw/main/transformer/diffusion_pytorch_model.safetensors.index.json -d /content/model/transformer -o diffusion_pytorch_model.safetensors.index.json && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/FLUX.1-dev-diffusers/raw/main/vae/config.json -d /content/model/vae -o config.json && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/FLUX.1-dev-diffusers/resolve/main/vae/diffusion_pytorch_model.safetensors -d /content/model/vae -o diffusion_pytorch_model.safetensors && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/FLUX.1-dev-diffusers/raw/main/model_index.json -d /content/model -o model_index.json    

COPY ./worker_runpod.py /content/worker_runpod.py
WORKDIR /content
CMD python worker_runpod.py
