"""
SDXL_Base - A class for generating images from text descriptions using the SDXL-Base model.
For more information, visit: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0
"""

import os
import torch
from diffusers import DiffusionPipeline
from ..base_model import BaseModel
from dotenv import load_dotenv
load_dotenv()
TRANSFORMERS_CACHE = os.getenv("TRANSFORMERS_CACHE")

class SDXL_Base(BaseModel):
    def __init__(self, device:str, variant="fp16", torch_dtype=torch.float16):
        """
        Initializes the SDXL_Base class with the specified computing device, variant, and torch data type.

        Parameters:
        - device: The computing device ('cpu' or 'cuda') for the model to run on. Defaults to 'cuda'.
        - variant: The variant of the model to use, influencing the precision and performance. Defaults to 'fp16'.
        - torch_dtype: The torch data type (e.g., torch.float16) for the model. Defaults to torch.float16.
        """
        self.model_pipe = DiffusionPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0",
            torch_dtype=torch.float16,
            use_safetensors=True,
            variant="fp16",
            cache_dir=TRANSFORMERS_CACHE
        )

        if device != "cpu":
            print(f"Moving model to GPU... device {device}")
            self.model_pipe.to(device)

    def generate(self, text_prompt, folder_path="./", filename="sdxl-base-image.jpeg",
                 num_inference_steps=50, guidance_scale=7.5):
        """
        Generates and saves an image based on the provided text prompt.

        Parameters:
        - text_prompt: The text prompt for guiding the image generation.
        - folder_path: The directory path where the generated image will be saved. Defaults to './'.
        - filename: The filename for the saved image, including its extension (e.g., 'image.jpeg'). Defaults to 'sdxl-base-image.jpeg'.
        - num_inference_steps: The number of inference steps to perform for image generation. Defaults to 50.
        - guidance_scale: The scale of guidance for adherence to the text prompt. Defaults to 7.5.

        Returns:
        The path to the saved image file. If the file already exists, the existing path is returned.
        """
        save_path = os.path.join(folder_path, filename)
        if os.path.exists(save_path):
            print(f"Image already exists at {save_path}")
            return save_path

        print(f"Generating image with caption: {text_prompt}")
        image = self.model_pipe(
            prompt=text_prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale
        ).images[0]

        image.save(save_path)
        return save_path
