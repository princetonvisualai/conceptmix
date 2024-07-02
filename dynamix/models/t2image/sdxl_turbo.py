""" 
SDXL-Turbo - A class for generating images from descriptions using the SDXL-Turbo model.
For more details, visit: https://huggingface.co/stabilityai/sdxl-turbo
"""

import os
from diffusers import AutoPipelineForText2Image
from ..base_model import BaseModel
import torch
from dotenv import load_dotenv
load_dotenv()
TRANSFORMERS_CACHE = os.getenv("TRANSFORMERS_CACHE")

class SDXL_Turbo(BaseModel):
    def __init__(self, device:str, variant="fp16", torch_dtype=torch.float32):
        """
        Initializes the SDXL_Turbo class with the specified computing device, variant, and torch data type.

        Parameters:
        - device: The computing device ('cpu' or 'cuda') for the model to run on. Defaults to 'cuda'.
        - variant: The variant of the model to use, affecting performance and precision. Defaults to 'fp16'.
        - torch_dtype: The torch data type (e.g., torch.float32) for the model. Defaults to torch.float32.
        """
        self.model_pipe = AutoPipelineForText2Image.from_pretrained(
            "stabilityai/sdxl-turbo", 
            torch_dtype=torch_dtype, 
            variant=variant, 
            cache_dir=TRANSFORMERS_CACHE
        )

        if device != "cpu":
            print(f"Moving model to GPU... device {device}")
            self.model_pipe.to(device)
    
    def generate(self, text_prompt, folder_path="./", filename="sdxl-turbo-image.jpeg", 
                 num_inference_steps=1, guidance_scale=0.0):
        """
        Generates and saves an image based on the provided text prompt.

        Parameters:
        - text_prompt: The text prompt for guiding the image generation.
        - folder_path: The directory path where the generated image will be saved. Defaults to './'.
        - filename: The filename for the saved image, including its extension (e.g., 'image.jpeg'). Defaults to 'sdxl-turbo-image.jpeg'.
        - num_inference_steps: The number of inference steps to perform for image generation. Defaults to 1, as recommended for SDXL-Turbo.
        - guidance_scale: The scale of guidance for adherence to the text prompt. Defaults to 0.0, as SDXL-Turbo may not require guidance scaling.

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
