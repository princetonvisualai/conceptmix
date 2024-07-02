try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
import os
import time
from utils import robustify_api_call, encode_image


class ImageToTextClient:
    def __init__(self, model_path):
        self.model_path = model_path
    
    def generate(self, image, prompt, **kwargs):
        pass

class OpenAIImageToTextClient(ImageToTextClient):
    def __init__(self, model_path):
        super().__init__(model_path)
        if OpenAI is None:
            raise ImportError("Please install the OpenAI Python package: pip install openai")
        self.client = OpenAI()
        self.generate = robustify_api_call(self._generate, attempt=10)

    def _generate(self, image, prompt, max_tokens=300, detail='high'):
        if image.startswith("http"): 
            image_url = {"url": image, 'detail': detail}
        else:
            extension = image.split(".")[-1]
            base64_image = encode_image(image)
            image_url = {"url": f"data:image/{extension};base64,{base64_image}", 'detail': detail}
        
        response = self.client.chat.completions.create(
            model=self.model_path,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": image_url},
                ]
            }],
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content

def get_image2text_client(model_path):
    if 'gpt' in model_path and 'vision' in model_path:
        return OpenAIImageToTextClient(model_path)
    else:
        raise ValueError(f"Model {model_path} not supported")
    

    