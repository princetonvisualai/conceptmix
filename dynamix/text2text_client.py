try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
import os
import time
from utils import robustify_api_call

class TextToTextClient:
    def __init__(self, model_path):
        self.model_path = model_path
    
    def generate(self, prompt, **kwargs):
        pass

class OpenAITextToTextClient(TextToTextClient):
    def __init__(self, model_path):
        super().__init__(model_path)
        if OpenAI is None:
            raise ImportError("Please install the OpenAI Python package: pip install openai")
        self.client = OpenAI()
        self.generate = robustify_api_call(self._generate, attempt=10)
    
    def _generate(self, prompt, n=1):
        response = self.client.chat.completions.create(
            model=self.model_path,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            n=n
        )
        if n == 1:
            text = response.choices[0].message.content
            return text
        else:
            texts = [data.message.content for data in response.choices]
            return texts

def get_text2text_client(model_path):
    if 'gpt' in model_path:
        return OpenAITextToTextClient(model_path)
    else:
        raise ValueError(f"Model {model_path} not supported")
    
if __name__ == "__main__":
    client = get_text2text_client("gpt-4")
    prompt = "Translate the following English text to French: 'Hello, how are you?'"
    print(client.generate(prompt))