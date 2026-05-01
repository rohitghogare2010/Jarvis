import torch
from diffusers import StableDiffusionPipeline, StableDiffusionUpscalePipeline
from PIL import Image
import os

class ImageGenerator:
    def __init__(self, cache_dir):
        self.cache_dir = cache_dir
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_id = "runwayml/stable-diffusion-v1-5"
        self.upscale_model_id = "stabilityai/stable-diffusion-x4-upscaler"

    def generate_base(self, prompt, negative_prompt=""):
        pipe = StableDiffusionPipeline.from_pretrained(self.model_id, torch_dtype=torch.float16 if self.device == "cuda" else torch.float32)
        pipe.to(self.device)
        
        image = pipe(prompt, negative_prompt=negative_prompt).images[0]
        return image

    def upscale_tiled(self, image, prompt):
        # Simplified tiled upscaling logic
        upscaler = StableDiffusionUpscalePipeline.from_pretrained(self.upscale_model_id, torch_dtype=torch.float16 if self.device == "cuda" else torch.float32)
        upscaler.to(self.device)
        
        # Real 8K/16K would require multiple upscale passes and tiling
        # Here we do one pass for demonstration
        upscaled_image = upscaler(prompt=prompt, image=image).images[0]
        return upscaled_image

    def generate_professional(self, prompt, character=None, style="realistic", quality="8k"):
        """
        Generates high-end professional images with supernatural/realistic/anime styles.
        """
        style_modifiers = {
            "realistic": "hyper-realistic, cinematic lighting, 8k resolution, highly detailed, professional photography, movie still",
            "anime": "high-quality anime style, studio ghibli inspired, vibrant colors, sharp lines, detailed background, 4k anime render",
            "supernatural": "mystical atmosphere, supernatural effects, glowing particles, ethereal lighting, epic fantasy, cinematic masterpiece",
            "movie": "hollywood movie style, anamorphic lens flares, color graded, dramatic lighting, high budget production"
        }
        
        full_prompt = prompt
        if character:
            full_prompt = f"Character: {character.name}, {character.appearance_desc}. {full_prompt}"
        
        full_prompt += f", {style_modifiers.get(style, style_modifiers['realistic'])}"
        
        if quality == "8k":
            full_prompt += ", ultra-high resolution, 8k"
        elif quality == "16k":
            full_prompt += ", 16k resolution, maximum detail, unreal engine 5 render"

        return self.generate_base(full_prompt)

    def generate_city_structure(self, city_name, prompt_details=""):
        full_prompt = f"Highly detailed architectural map and 3D structure of {city_name}, {prompt_details}, realistic city layout, 8k resolution, satellite view mixed with street level detail"
        return self.generate_base(full_prompt)

    def save_image(self, image, filename):
        path = os.path.join(self.cache_dir, filename)
        image.save(path)
        return path
