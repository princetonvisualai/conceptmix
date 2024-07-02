
"""
SDXL_2_1 - A class for generating images from text descriptions using the Stable Diffusion 2.1 model.
For detailed information, visit: https://huggingface.co/stabilityai/stable-diffusion-2-1
"""

import os
import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from ..base_model import BaseModel
from dotenv import load_dotenv
load_dotenv()

TRANSFORMERS_CACHE = os.getenv("TRANSFORMERS_CACHE")

class SDXL_2_1(BaseModel):
    def __init__(self, device:str, torch_dtype=torch.float16):
        """
        Initializes the SDXL_2_1 class with the specified computing device and torch data type.

        Parameters:
        - device: The computing device ('cpu' or 'cuda') for the model to run on. Defaults to 'cuda'.
        - torch_dtype: The torch data type (e.g., torch.float16) for the model. Defaults to torch.float16.
        """
        super().__init__()  # Base class initializer
        self.model_id = "stabilityai/stable-diffusion-2-1"
        self.model_pipe = StableDiffusionPipeline.from_pretrained(
            self.model_id, 
            torch_dtype=torch_dtype, 
            cache_dir=TRANSFORMERS_CACHE
        )
        
        # Update the scheduler for improved efficiency
        self.model_pipe.scheduler = DPMSolverMultistepScheduler.from_config(
            self.model_pipe.scheduler.config
        )
        
        if device != "cpu":
            print(f"Moving model to GPU... device {device}")
            self.model_pipe.to(device)

    def generate(self, text_prompt, folder_path="./", filename="sdxl-2-1-image.png",
                 num_inference_steps=50, guidance_scale=7.5):
        """
        Generates and saves an image based on the provided text prompt.

        Parameters:
        - text_prompt: The text prompt for guiding the image generation.
        - folder_path: The directory path where the generated image will be saved. Defaults to './'.
        - filename: The filename for the saved image, including its extension (e.g., 'image.png'). Defaults to 'sdxl-2-1-image.png'.
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
