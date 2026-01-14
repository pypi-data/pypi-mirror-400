from diffsynth.pipelines.z_image import (
    ZImagePipeline, ModelConfig,
    ZImageUnit_Image2LoRAEncode, ZImageUnit_Image2LoRADecode
)
from modelscope import snapshot_download
from safetensors.torch import save_file
import torch, os
from PIL import Image

# Use `vram_config` to enable LoRA hot-loading
vram_config = {
    "offload_dtype": torch.bfloat16,
    "offload_device": "cuda",
    "onload_dtype": torch.bfloat16,
    "onload_device": "cuda",
    "preparing_dtype": torch.bfloat16,
    "preparing_device": "cuda",
    "computation_dtype": torch.bfloat16,
    "computation_device": "cuda",
}

# Load models
pipe = ZImagePipeline.from_pretrained(
    torch_dtype=torch.bfloat16,
    device="cuda",
    model_configs=[
        ModelConfig(model_id="Tongyi-MAI/Z-Image-Omni-Base", origin_file_pattern="transformer/*.safetensors", **vram_config),
        ModelConfig(model_id="Tongyi-MAI/Z-Image-Omni-Base", origin_file_pattern="siglip/model.safetensors"),
        ModelConfig(model_id="Tongyi-MAI/Z-Image-Turbo", origin_file_pattern="text_encoder/*.safetensors"),
        ModelConfig(model_id="Tongyi-MAI/Z-Image-Turbo", origin_file_pattern="vae/diffusion_pytorch_model.safetensors"),
        ModelConfig(model_id="DiffSynth-Studio/General-Image-Encoders", origin_file_pattern="SigLIP2-G384/model.safetensors"),
        ModelConfig(model_id="DiffSynth-Studio/General-Image-Encoders", origin_file_pattern="DINOv3-7B/model.safetensors"),
        ModelConfig("/mnt/nas1/duanzhongjie.dzj/dev3_zi2L/DiffSynth-Studio/models/train/ema_v30_0.9_0108.safetensors"),
    ],
    tokenizer_config=ModelConfig(model_id="Tongyi-MAI/Z-Image-Turbo", origin_file_pattern="tokenizer/"),
)


from diffsynth.core.data.operators import ImageCropAndResize
processor_highres = ImageCropAndResize(height=1024, width=1024)
for style_id in range(3, 12):
    images = [Image.open(f"/mnt/nas1/duanzhongjie.dzj/dev3_zi2L/DiffSynth-Studio/data/style/{style_id}/{i}") for i in os.listdir(f"/mnt/nas1/duanzhongjie.dzj/dev3_zi2L/DiffSynth-Studio/data/style/{style_id}")]
    os.makedirs(f"data/style/{style_id}", exist_ok=True)
    for image_id, image in enumerate(images):
        image = processor_highres(image)
        image.save(f"data/style/{style_id}/{image_id}.jpg")
    images = [Image.open(f"data/style/{style_id}/{i}.jpg") for i in range(len(images))]

    with torch.no_grad():
        embs = ZImageUnit_Image2LoRAEncode().process(pipe, image2lora_images=images)
        lora = ZImageUnit_Image2LoRADecode().process(pipe, **embs)["lora"]

    prompts = ["a cat", "a dog", "a girl"]
    for prompt_id, prompt in enumerate(prompts):
        negative_prompt = "泛黄，发绿，模糊，低分辨率，低质量图像，扭曲的肢体，诡异的外观，丑陋，AI感，噪点，网格感，JPEG压缩条纹，异常的肢体，水印，乱码，意义不明的字符"
        image = pipe(prompt=prompt, negative_prompt=negative_prompt, seed=0, cfg_scale=7, num_inference_steps=50, positive_only_lora=lora, sigma_shift=8)
        image.save(f"data/style_out/1/image_lora_{style_id}_{prompt_id}.jpg")
