import base64
import requests
import json
from openai import AzureOpenAI
import os
import math

from dynamix.utils import robusify_Azure_api_call


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def gpt_grading(image_path, full_sentence, question):
    base64_image = encode_image(image_path)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-4-turbo",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{question} Respond \"Yes\" or \"No\"."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 1,
        "temperature": 0,
        # "top_logprobs": 10,
        # "logprobs": True
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    try:
        answer = response.json()['choices'][0]['message']['content']
        # print(answer)
        if "Yes" in answer:
            score = 1
        else:
            score = 0
    except:
        print("Error in response")
        score = 0
    print(score)
    return score
    

def gpt_grading_azure(logprobs, image_path, full_sentence, question):
    base64_image = encode_image(image_path)


    model = "gpt-4o-2024-05-13"
    robust_Azure_chat_completion = robusify_Azure_api_call(model=model)

    # response = client.chat.completions.create(
    response = robust_Azure_chat_completion(
        # model=deployment_name,
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{question} Respond \"Yes\" or \"No\"."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=1, 
        temperature=0,
        # top_logprobs=5,
        # logprobs=True
    )

    try:
        answer = json.loads(response.json())['choices'][0]['message']['content']

        if logprobs:
            logprobility = json.loads(response.json())['choices'][0]['logprobs']['content'][0]['top_logprobs']
            for item in logprobility:
                if "Yes" == item['token']:
                    score = math.exp(item['logprob'])
        else:
            if "Yes" in answer:
                score = 1
            else:
                score = 0
    except:
        print("Error in response")
        score = 0
    print(score)
    return score

def gpt_grading_azure_two(logprobs, image_path, full_sentence, question):
    base64_image = encode_image(image_path)
    client = AzureOpenAI(
    # add your api information here
    ) #north-central-us, 4o


    model = "gpt-4o-2024-05-13"

    response = client.chat.completions.create(
        # model=deployment_name,
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{question} Respond \"Yes\" or \"No\"."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=1, 
        temperature=0,
        # top_logprobs=5,
        # logprobs=True
    )

    try:
        # answer = response.json()['choices'][0]['message']['content']
        answer = json.loads(response.json())['choices'][0]['message']['content']

        if logprobs:
            logprobility = json.loads(response.json())['choices'][0]['logprobs']['content'][0]['top_logprobs']
            for item in logprobility:
                if "Yes" == item['token']:
                    score = math.exp(item['logprob'])
        else:
            if "Yes" in answer:
                score = 1
            else:
                score = 0
    except:
        print("Error in response")
        score = 0
    print(score)
    return score


