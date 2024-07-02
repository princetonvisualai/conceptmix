"""
The module defines the DeepFloyd_I_XL_v1 class for generating images from text prompts using the 
DeepFloyd-I-XL-v1 model, a part of the Hugging Face Diffusers library.

To access this model, you need to be authenticated, please visit https://huggingface.co/DeepFloyd/IF-I-XL-v1.0 for instructions to authenticate and access the gated model.
"""

import os
import torch
from diffusers import DiffusionPipeline
from diffusers.utils import pt_to_pil
from ..base_model import BaseModel
from dotenv import load_dotenv
load_dotenv()

TRANSFORMERS_CACHE = os.getenv("TRANSFORMERS_CACHE")

class DeepFloyd_I_XL_v1(BaseModel):
    """
    DeepFloyd_I_XL_v1 facilitates image generation from text prompts through a multi-stage diffusion process.
    This class leverages pre-trained models from Hugging Face's Diffusers library.
    """

    def __init__(self, device: str):
        """
        Initializes the model pipeline components and configures them for the specified device.
        
        Parameters
        - device: The computing device ('cpu' or 'cuda') the model should run on. It determines whether to use GPU acceleration if available.
        """
        super().__init__()  # Initialize base class
        
        print("Loading DeepFloyd-I-XL-v1 model...")
        # Stage 1 model initialization
        self.stage_1 = DiffusionPipeline.from_pretrained(
            "DeepFloyd/IF-I-XL-v1.0",
            variant="fp16",
            torch_dtype=torch.float16,
            cache_dir=os.getenv("TRANSFORMERS_CACHE")
        )

        # Stage 2 model initialization
        self.stage_2 = DiffusionPipeline.from_pretrained(
            "DeepFloyd/IF-II-L-v1.0",
            text_encoder=None,
            variant="fp16",
            torch_dtype=torch.float16,
            cache_dir=TRANSFORMERS_CACHE
        )

        # Device configuration
        if device == "cpu":
            self.stage_1.enable_model_cpu_offload()
            self.stage_2.enable_model_cpu_offload()
        else:
            self.stage_1.to(device)
            self.stage_2.to(device)
        
        print("Finished loading models.")

    def generate(self, text_prompt, seed=0, folder_path=None, filename=None, noise_level=100):
        """
        Generates an image based on a text prompt and saves it to the specified location.
        
        Parameters:
        - text_prompt: The text prompt guiding the image generation.
        - seed: Seed for random number generation to ensure reproducible results.
        - folder_path: The directory where the generated image will be saved.
        - filename: The name for the saved image file, including its file extension (e.g., 'image.jpg').
        - noise_level: The noise level applied during image generation (currently unused in this implementation).
        
        @returns The file path to the saved image. If the file already exists, it returns the existing path.
        """
        save_path = os.path.join(folder_path, filename)
        if os.path.exists(save_path):
            print(f"Image already exists at {save_path}")
            return save_path

        # Generate image from text prompt
        prompt_embeds, negative_embeds = self.stage_1.encode_prompt(text_prompt)
        generator = torch.manual_seed(seed)

        # Initial image generation with stage 1
        image = self.stage_1(
            prompt_embeds=prompt_embeds, 
            negative_prompt_embeds=negative_embeds, 
            generator=generator, 
            output_type="pt"
        ).images

        # Image refinement with stage 2
        image = self.stage_2(
            image=image, 
            prompt_embeds=prompt_embeds, 
            negative_prompt_embeds=negative_embeds, 
            generator=generator, 
            output_type="pt"
        ).images

        # Save the final image
        pt_to_pil(image)[0].save(save_path)

        return save_path
