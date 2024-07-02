import os
import re
import json
import requests
import argparse
import torch
from diffusers import StableDiffusionPipeline, DiffusionPipeline, PixArtAlphaPipeline
from models.t2image import get_model_class
from openai import AzureOpenAI


DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def get_model(name):
    if name == "DeepFloyd_I_XL_v1":
        return get_model_class('DeepFloyd_I_XL_v1')(device=DEVICE)
    elif name == "SDXL_Turbo":
        return get_model_class('SDXL_Turbo')(device=DEVICE)
    elif name == "SDXL_Base":
        return get_model_class('SDXL_Base')(device=DEVICE)
    elif name == "SDXL_2_1":
        return get_model_class('SDXL_2_1')(device=DEVICE)
    else:
        raise ValueError(f"Model {name} not found")

def generate_and_save_image(args, k, prompt, model, model_instance, categories, skills, questions, index, output_dir="results"):
    model_dir = os.path.join(output_dir, model, str(k))
    os.makedirs(model_dir, exist_ok=True)
    filename = str(index) + re.sub(r'\W+', '', prompt.replace(" ", "_"))[:50] + ".png"
    file_path = os.path.join(model_dir, filename)

    if model.startswith("dall-e"):
        client = model_instance
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            n=1,
        )
        image_url = response.data[0].url
        image_response = requests.get(image_url)
        with open(file_path, "wb") as file:
            file.write(image_response.content)
    elif model.startswith("stable-diffusion") or model.startswith("playground") or model.startswith("PixArt"):
        pipe = model_instance.to(DEVICE)
        image = pipe(prompt=prompt).images[0]
        image.save(file_path)
    elif model.startswith("DeepFloyd") or model.startswith("SDXL") or model.startswith("Midjourney"):
        generation_model = model_instance
        generation_model.generate(text_prompt=prompt, folder_path=model_dir, filename=filename)
    else:
        raise NotImplementedError(f"Model {model} not implemented")

    print(f"Image saved as {file_path}.")


    if args.specified_skill:
        json_file_path = os.path.join(model_dir, f"{args.specified_skill}.json")
    else:
        json_file_path = os.path.join(model_dir, "result.json")
    data = {
        "num_skills": k,
        "prompt": prompt,
        "image_path": file_path,
        "categories": categories,
        "skill": skills,
        "question": questions
    }

    if os.path.exists(json_file_path):
        with open(json_file_path, "r") as json_file:
            try:
                existing_data = json.load(json_file)
                if isinstance(existing_data, dict):
                    existing_data = [existing_data]
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    existing_data.append(data)

    with open(json_file_path, "w") as json_file:
        json.dump(existing_data, json_file, indent=4)

    print(f"Prompt, image path, categories, and skills appended to {json_file_path}.")

def main(args):
    k = args.num_skills

    output_dir = args.output_dir if args.specified_skill is None else f"{args.output_dir}/{args.specified_skill}"
    os.makedirs(output_dir, exist_ok=True)

    intermediate_file_path = args.intermediate_file_path
    if not os.path.exists(intermediate_file_path):
        raise FileNotFoundError(f"File {intermediate_file_path} not found.")
    
    with open(intermediate_file_path, 'r') as f:
        data = json.load(f)

    # models = [
    #     "playground-v2.5-1024px-aesthetic", 
    #     "DeepFloyd_I_XL_v1", 
    #     "SDXL_Turbo", 
    #     "SDXL_2_1", 
    #     "SDXL_Base", 
    #     "stable-diffusion", 
    #     "dall-e-3",
    #     "PixArt-XL-2-1024-MS"
    # ]

    model = args.model
    print(f"Initializing model '{model}'...")
    if model.startswith("dall-e"):
        model_instance = AzureOpenAI(
            # add your api information here
        )
    elif model.startswith("stable-diffusion"):
        model_instance = StableDiffusionPipeline.from_pretrained("CompVis/stable-diffusion-v1-4", torch_dtype=torch.float16)
    elif model.startswith("playground"):
        model_instance = DiffusionPipeline.from_pretrained("playgroundai/playground-v2.5-1024px-aesthetic", torch_dtype=torch.float16, variant="fp16")
    elif model.startswith("PixArt"):
        model_instance = PixArtAlphaPipeline.from_pretrained("PixArt-alpha/PixArt-XL-2-1024-MS", torch_dtype=torch.float16)
    elif model.startswith("DeepFloyd") or model.startswith("SDXL") or model.startswith("Midjourney"):
        model_instance = get_model(model)
    else:
        raise NotImplementedError(f"Model {model} not implemented")

    print(f"Generating images for model '{model}'...")
    for entry in data:
        sentence = entry['sentence']
        categories = entry['categories']
        skills = entry['skills']
        question = entry['question']
        index = entry['index']
        
        generate_and_save_image(args, k, sentence, model, model_instance, categories, skills, question, index, output_dir)
  

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate images based on provided skills.")
    parser.add_argument("--num_skills", type=int, default=1, help="Number of skills")
    parser.add_argument("--specified_skill", type=str, default=None, help="Specify a skill to generate images for")
    parser.add_argument("--output_dir", type=str, default="all/1_results", help="Output directory for generated images")
    parser.add_argument("--config_path", type=str, default="./config", help="Path to the config files")
    parser.add_argument("--intermediate_file_path", type=str, default="all/0_sentence_collection/100_sentences_k=1.json", help="Path to the intermediate file")
    parser.add_argument("--model", type=str, default="playground-v2.5-1024px-aesthetic", help="Model to use for image generation")

    args = parser.parse_args()
    main(args)
