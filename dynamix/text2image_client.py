try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
import os
import time
from utils import robustify_api_call, save_image
import requests, re
from diffusers import StableDiffusionPipeline
import torch

class TextToImageClient:
    def __init__(self, model_path):
        self.model_path = model_path
    
    def generate(self, prompt, **kwargs):
        pass

class OpenAITextToImageClient(TextToImageClient):
    def __init__(self, model_path):
        super().__init__(model_path)
        if OpenAI is None:
            raise ImportError("Please install the OpenAI Python package: pip install openai")
        self.client = OpenAI()
        self.generate = robustify_api_call(self._generate, attempt=10)
    
    def _generate(self, prompt, size='1024x1024', quality='standard', n=1):
        response = self.client.images.generate(
            model=self.model_path,
            prompt=prompt,
            size=size,
            quality=quality,
            n=n,
        )
        if n == 1:
            image_url = response.data[0].url
            return image_url
        else:
            image_urls = [data.url for data in response.data]
            return image_urls

class StableDiffusionTextToImageClient(TextToImageClient):
    def __init__(self, model_path, device="cuda"):
        super().__init__(model_path)
        model_id = "CompVis/stable-diffusion-v1-4"
        self.pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
        self.pipe = self.pipe.to(device)
    
    def generate(self, prompt):
        image = self.pipe(prompt).images[0]
        return image

def get_text2image_client(model_path, **kwargs):
    if 'dall-e' in model_path:
        return OpenAITextToImageClient(model_path, **kwargs)
    if model_path.startswith("stable-diffusion"):
        return StableDiffusionTextToImageClient(model_path, **kwargs)
    else:
        raise ValueError(f"Model {model_path} not supported")
    
if __name__ == "__main__": 
    

    client = get_text2image_client("stable-diffusion-v1-4")
    prompt = "A cute cat with wings sitting on a cloud"
    image = client.generate(prompt)
    filename = re.sub(r'\W+', '', prompt.replace(" ", "_"))[:50] + ".png"
    file_path = os.path.join('.', filename)
    save_image(image, file_path)


    print(f"Image saved as {file_path}.")