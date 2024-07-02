import json
import os
# from openai import OpenAI
from openai import AzureOpenAI
import os
import json
import random
import time
import base64
import requests
import inflect
inflect_engine = inflect.engine()

def load_all_configs(config_path, specified_skill=None):
    config_files = [f for f in os.listdir(config_path) if f.endswith('.json')]

    skills, descriptions, categories = [], [], []

    for config_file in config_files:
        file_path = os.path.join(config_path, config_file)
        with open(file_path, 'r') as file:
            data = json.load(file)
            for skill in data['skill'].keys():
                description = data['skill'][skill]
                if not description:
                    description = data['description'].format(skill=skill)
                skills.append(skill)
                descriptions.append(description)
                categories.append(data['category'])

    return skills, descriptions, categories

def load_configs(k, config_path, specified_skill=None):
    # config_files = ['object.json'] + [f for f in os.listdir(config_path) if f.endswith('.json')]
    config_files = [f for f in os.listdir(config_path) if f.endswith('.json')]
    if k > len(config_files):
        raise ValueError("k is larger than or equal to the available config files, leaving no files for additional words")

    descriptions = []
    skills = []
    categories = []
    
    if not specified_skill:
        random_config_files = [specified_skill + '.json']
    else:
        raise NotImplementedError
        # note that random.sample can only select from two different configs, 
        # if we allow same configs, we need to use random.choices(config_files, k=k)
    # debug:


    with open(os.path.join(config_path, 'object.json'), 'r') as file:
        data = json.load(file)
        object = random.choice(list(data['skill'].keys()))
        print("object:", object)

    for i in range(k):
        file_path = os.path.join(config_path, random_config_files[i])
        with open(file_path, 'r') as file:
            data = json.load(file)
            skill = random.choice(list(data['skill'].keys()))
            
            description = data['skill'][skill]
            if not description:
                description = data['description'].format(skill=skill, object=object)
            skills.append(skill)
            descriptions.append(description)
            categories.append(data['category'])
    print("skills: [" + ", ".join(f"{category}: '{element}'" for category, element in zip(categories, skills)) + "]")
    print("descriptions: [" + ", ".join(f"'{element}'" for element in descriptions) + "]")
    print("=====")
    return skills, descriptions, categories

def load_random_value(config_path, config_file):
    file_path = os.path.join(config_path, config_file)
    with open(file_path, 'r') as file:
        data = json.load(file)
        skill = random.choice(list(data['skill'].keys()))
        description = data['skill'][skill]
        if not description:
            description = data['description']
        category = data['category']
    return skill, description, category

def load_sequential_value(config_path, config_file):
    file_path = os.path.join(config_path, config_file)
    skill_list = []
    
    with open(file_path, 'r') as file:
        data = json.load(file)
        total_skills = len(data['skill'])
        for i in range(len(data['skill'])):
            skill = list(data['skill'].keys())[i]
            skill_list.append(skill)
        description = data['skill'][skill]
        if not description:
            description = data['description']
        category = data['category']
    return total_skills, skill_list, description, category

def load_configs_new(chat_api, k, config_path, specified_skill=None, object_prob=0.25):
    if specified_skill:
        assert(k==1)
    config_files = [f for f in os.listdir(config_path) if f.endswith('.json') and f != 'object.json']

    # decide object number
    num_objects = 1
    if not specified_skill:
        for i in range(k):
            if random.random() < object_prob:
                num_objects += 1
    
    k_other = k + 1 - num_objects
    if specified_skill is not None:
        random_config_files = [specified_skill + '.json']
    else:
        random_config_files = random.choices(config_files, k=k_other)

    max_count = lambda x: max([x.count(i) for i in set(x)]) if len(x) > 0 else 0

    while max_count(random_config_files) > num_objects or random_config_files.count('styles.json') > 1:
        random_config_files = random.choices(config_files, k=k_other)


    skills = []
    descriptions = []
    categories = []
    initail_config = {'objects': []}
    # generate object
    for i in range(num_objects):
        skill, description, category = load_random_value(config_path, 'object.json')
        # make sure skill is not repeated
        while skill in skills:
            skill, description, category = load_random_value(config_path, 'object.json')
        skill_pl = inflect_engine.plural(skill)
        description = description.format(skill=skill, skills=skill_pl)
        initail_config['objects'].append({'id': i+1, 'item': skill})
        skills.append(skill)
        descriptions.append(description)
        categories.append(category)
    
    sequential = True if specified_skill else False
    for i in range(k_other):
        skill, description, category = load_random_value(config_path, random_config_files[i])
        if category == 'style':
            initail_config['style'] = skill
            description = description.format(skill=skill)
            skills.append(skill)
            descriptions.append(description)
            categories.append(category)
        elif category == 'spatial':
            if 'relation' not in initail_config:
                initail_config['relation'] = []
            initail_config['relation'].append({'name': skill, 'description': description, 'ObjectA_id': '?', 'ObjectB_id': '?'})
        else:
            idx = random.choice(range(num_objects))
            while category in initail_config['objects'][idx]:
                idx = random.choice(range(num_objects))
            initail_config['objects'][idx][category] = skill
            object_single = initail_config['objects'][idx]['item']
            object_plural = inflect_engine.plural(object_single)
            description = description.format(skill=skill, object=object_single, objects=object_plural)
            skills.append(skill)
            descriptions.append(description)
            categories.append(category)

    
    model = "gpt-4o-2024-05-13"
    refine_config_prompt = 'I am trying to create an image containing exactly the following things in a JSON format:\n' + json.dumps(initail_config) + '\n' + 'Could you check if there is "?" left in the JSON? If so, could you fill in the missing part? Make sure it makes sense when you fill the missing part. Do not fill in anything else unless it is indicated by "?". You may add additional objects, but only in the following two cases:\n * It is needed to fill in any "?" (Note when you fill "?", you should use existing objects first. If you still choose to add an object, explain why the existing objects cannot fulfill the need.); or \n * If there is an attribute specified in the JSON that contains relative information (e.g. "size") and there is no other object for reference. (The reason for adding an object for this case is because one cannot tell whether an object is huge without any other object in the image, but we are fine if there is no such attribute mentioned in the JSON. Note other existing object in JSON can be used for reference, and the reference object does not need to be the same object. If you still choose to add an object, explain why the existing objects cannot fulfill the need.)\nDO NOT add any object if none of the above situation is strictly satisifed, and DO NOT try to improve the image in other ways. If you choose to add an object, make sure it fits in the image naturally. Please only add the necessary objects, and the added objects should only have "id" and "item" specified, and should be appended to "objects".'
    completion = chat_api(
        model = model,
        messages = [
            {"role": "user", "content": refine_config_prompt}
        ]
    )
    full_response = completion.choices[0].message.content
    # print(refine_config_prompt)
    print(json.dumps(initail_config))
    print(full_response)
    json_only_prompt = 'Could you respond only the JSON?'
    completion = chat_api(
        model = model,
        messages = [
            {"role": "user", "content": refine_config_prompt},
            {"role": "assistant", "content": full_response},
            {"role": "user", "content": json_only_prompt}
        ]
    )
    json_response = completion.choices[0].message.content
    # print(json_response)
    # check if it starts with ```json and ends with ```, remove if so
    if json_response.startswith('```json'):
        json_response = json_response[7:]
    if json_response.endswith('```'):
        json_response = json_response[:-3]
    try:
        refined_config = json.loads(json_response)
    except:
        print("json_response:", json_response)
        raise ValueError("The refined config is not a valid JSON format")

    # check if id is 1, 2, 3, ...
    for i, object in enumerate(refined_config['objects']):
        assert(int(object['id']) == i + 1)
    extra_skills = []
    extra_descriptions = []
    extra_categories = []
    for object in refined_config['objects'][num_objects:]:
        extra_skills.append(object['item'])
        extra_descriptions.append(f"the image contain one {object['item']}.")
        extra_categories.append('object')
    if 'relation' in refined_config:
        for relation in refined_config['relation']:
            objectA = refined_config['objects'][int(relation['ObjectA_id'])-1]['item']
            objectB = refined_config['objects'][int(relation['ObjectB_id'])-1]['item']
            if objectA == objectB:
                objectB = "another " + objectB
            description = relation['description'].format(ObjectA=objectA, ObjectB=objectB)
            skills.append(relation['name'])
            descriptions.append(description)
            categories.append('spatial')

    return skills, descriptions, categories, refined_config


def load_configs_sequentially(curr_skill, curr_description, curr_category, client, k, config_path, specified_skill=None, object_prob=0.25):
    # this function can be integrated into load_configs_new later
    if specified_skill:
        assert(k==1)
    
    k_other = 1
    num_objects = 1
    random_config_files = [specified_skill + '.json']

    skills = []
    descriptions = []
    categories = []
    initail_config = {'objects': []}
    # generate object
    for i in range(num_objects):
        skill, description, category = load_random_value(config_path, 'object.json')
        # make sure skill is not repeated
        while skill in skills:
            skill, description, category = load_random_value(config_path, 'object.json')
        skill_pl = inflect_engine.plural(skill)
        description = description.format(skill=skill, skills=skill_pl)
        initail_config['objects'].append({'id': i+1, 'item': skill})
        skills.append(skill)
        descriptions.append(description)
        categories.append(category)
    
    for i in range(k_other):
        skill, description, category = curr_skill, curr_description, curr_category,
        if category == 'style':
            initail_config['style'] = skill
            description = description.format(skill=skill)
            skills.append(skill)
            descriptions.append(description)
            categories.append(category)
        elif category == 'spatial':
            if 'relation' not in initail_config:
                initail_config['relation'] = []
            initail_config['relation'].append({'name': skill, 'description': description, 'ObjectA_id': '?', 'ObjectB_id': '?'})
        else:
            idx = random.choice(range(num_objects))
            while category in initail_config['objects'][idx]:
                idx = random.choice(range(num_objects))
            initail_config['objects'][idx][category] = skill
            object_single = initail_config['objects'][idx]['item']
            object_plural = inflect_engine.plural(object_single)
            description = description.format(skill=skill, object=object_single, objects=object_plural)
            skills.append(skill)
            descriptions.append(description)
            categories.append(category)

    
    model = "gpt-4o-2024-05-13"
    refine_config_prompt = 'I am trying to create an image containing exactly the following things in a JSON format:\n' + json.dumps(initail_config) + '\n' + 'Could you check if there is "?" left in the JSON? If so, could you fill in the missing part? Make sure it makes sense when you fill the missing part. Do not fill in anything else unless it is indicated by "?". You may add additional objects, but only in the following two cases:\n * It is needed to fill in any "?" (Note when you fill "?", you should use existing objects first. If you still choose to add an object, explain why the existing objects cannot fulfill the need.); or \n * If there is an attribute specified in the JSON that contains relative information (e.g. "size") and there is no other object for reference. (The reason for adding an object for this case is because one cannot tell whether an object is huge without any other object in the image, but we are fine if there is no such attribute mentioned in the JSON. Note other existing object in JSON can be used for reference, and the reference object does not need to be the same object. If you still choose to add an object, explain why the existing objects cannot fulfill the need.)\nDO NOT add any object if none of the above situation is strictly satisifed, and DO NOT try to improve the image in other ways. If you choose to add an object, make sure it fits in the image naturally. Please only add the necessary objects, and the added objects should only have "id" and "item" specified, and should be appended to "objects".'
    completion = client.chat.completions.create(
        model = model,
        messages = [
            {"role": "user", "content": refine_config_prompt}
        ]
    )
    full_response = completion.choices[0].message.content
    # print(refine_config_prompt)
    print(json.dumps(initail_config))
    print(full_response)
    json_only_prompt = 'Could you respond only the JSON?'
    completion = client.chat.completions.create(
        model = model,
        messages = [
            {"role": "user", "content": refine_config_prompt},
            {"role": "assistant", "content": full_response},
            {"role": "user", "content": json_only_prompt}
        ]
    )
    json_response = completion.choices[0].message.content
    # print(json_response)
    # check if it starts with ```json and ends with ```, remove if so
    if json_response.startswith('```json'):
        json_response = json_response[7:]
    if json_response.endswith('```'):
        json_response = json_response[:-3]
    try:
        refined_config = json.loads(json_response)
    except:
        print("json_response:", json_response)
        raise ValueError("The refined config is not a valid JSON format")

    # check if id is 1, 2, 3, ...
    for i, object in enumerate(refined_config['objects']):
        assert(int(object['id']) == i + 1)
    extra_skills = []
    extra_descriptions = []
    extra_categories = []
    for object in refined_config['objects'][num_objects:]:
        extra_skills.append(object['item'])
        extra_descriptions.append(f"the image contain one {object['item']}.")
        extra_categories.append('object')
    if 'relation' in refined_config:
        for relation in refined_config['relation']:
            objectA = refined_config['objects'][int(relation['ObjectA_id'])-1]['item']
            objectB = refined_config['objects'][int(relation['ObjectB_id'])-1]['item']
            if objectA == objectB:
                objectB = "another " + objectB
            description = relation['description'].format(ObjectA=objectA, ObjectB=objectB)
            skills.append(relation['name'])
            descriptions.append(description)
            categories.append('spatial')

    return skills, descriptions, categories, refined_config

def generate_sentence(chat_api, skills, descriptions, json_config=None):
    k = len(descriptions)
    model = "gpt-4o-2024-05-13"
    length = k * 3 + 4
    prompt = "Make up a human-annotated description of an image that describe the following properties (meaning you can infer these properties from the description):\n" 
    for description in descriptions:
        prompt += f"* {description}\n"
    # prompt += f"The caption should be around {length} words long. "
    if json_config:
        prompt += "As a reference, I contructed a JSON containing all the information from the properties and some additional information that you should incorperate into your description:\n```json" + json.dumps(json_config) + "```\n"
    prompt += "Describe the image in an objective and unbiased way. Keep the description clear and unambiguous, synthesize the objects in a clever and clean way, so people can roughly picture the scene from your description. DO NOT introduce unnecessary objects and unnecessary description of the objects beyond the given properties and JSON. If there is an interaction between two objects, make sure the two objects are distinguishable. Avoid any descriptions involving group of objects, or ambiguous number of objects like \"at least one\", \"one or more\", or \"several\". Do not add subjective judgments about the image, it should be as factual as possible. Do not use fluffy, poetic language, or any words beyond elementry school level. Respond \"WRONG\" and explain if the properties have obvious issues or conflicts, or if it is hard to realize them in an image. Otherwise, respond only with the caption itself. "
    completion = chat_api(
        # model="gpt-4",
        model=model,
        messages=[
            {"role": "user", "content": prompt},
        ]
    )
    sentence = completion.choices[0].message.content
    if sentence.startswith("WRONG"):
        print("sentence:", sentence)
        return sentence, None
    verification = "Could you read your caption again and verify if it makes sense in a very loose sense (e.g., a person cannot be triangle shaped, but a cloud can be square-shaped and a tree can be rectangle-shaped)? If yes, respond with the exact same caption. If not, respond with \"WRONG\" and explain why."
    completion = chat_api(
        model=model,
        messages=[
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": sentence},
            {"role": "user", "content": verification}
        ]
    )
    final_sentence = completion.choices[0].message.content
    if final_sentence.startswith("WRONG"):
        print("final_sentence:", final_sentence)
        return final_sentence, None
    


    if json_config:
        question_generation = f"A student just draw a picture based on your description. Can you help me verify whether the student did a good job? Specifically, I want to know if the image follows your description and also follows the properties I mentioned earlier. You should ask me one yes or no question for each property, and I will tell you if they are satisfied. For example, for properties like \"the image contains one or more {skills[0]}\", the corresponding question should be \"Does the image contain {skills[0]}?\". Respond only the {k} questions, one for each property, in the same order of the properties, and each on a new line."
    else:
        question_generation = f"A student just draw a picture based on your description. Can you help me verify whether the student did a good job? Specifically, I want to know if the image follows your description and also follows the propertied I mentioned earlier. You should ask me one yes or no question for each property, and I will tell you if they are satisfied. Because the wording of your desciption might be slightly different different from the properties, please stick to the wording of your desciption when you ask the questions. For example, you should avoid using the word \"object\", and the first question should be \"Does the image contain {skills[0]}?\". Note the properties do not have information duplication, please make sure the questions do not have information duplication as well. Respond only the {k} questions, one for each property, in the same order of the properties, and each on a new line."
    completion = chat_api(
        model=model,
        messages=[
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": sentence},
            # {"role": "user", "content": verification},
            # {"role": "assistant", "content": final_sentence},
            {"role": "user", "content": question_generation}
        ]
    )
    questions = completion.choices[0].message.content
    print("=====")
    print("final_sentence:", final_sentence)
    print("=====")
    print("questions: \n" + questions)
    print("=====")
    
    return final_sentence, questions.split('\n')


def robustify_api_call(func, attempt=10):
    def wrapper(*args, **kwargs):
        for i in range(attempt):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"Attempt {i+1} failed: {e}", flush=True)
                time.sleep(2**i)
        raise Exception(f"Failed after {attempt} attempts")
    return wrapper

def robusify_api_call_multiple_func(funcs, attempt=10):
    def wrapper(*args, **kwargs):
        for i in range(attempt):
            for idx, func in enumerate(funcs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Attempt {i+1} failed with {idx}-th client: {e}", flush=True)
            time.sleep(10 * (2**i))
        raise Exception(f"Failed after {attempt} attempts")
    return wrapper

def load_Azure_clients(model='gpt-4o-2024-05-13'):
    if model == 'gpt-4o-2024-05-13':
        clients = [
            AzureOpenAI(
                azure_endpoint=endpoint,
                api_key=api_key,
                api_version='2024-04-01-preview'
            ) for endpoint, api_key in zip([
                # add your api information here
            ],
            [
                # add your api information here
            ])
        ]
        return clients
    else:
        raise ValueError("Model not supported")
    
def robusify_Azure_api_call(model='gpt-4o-2024-05-13'):
    clients = load_Azure_clients(model)
    return robusify_api_call_multiple_func([client.chat.completions.create for client in clients])

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
def save_image(image, file_path):
    if image.startswith("http"):
        image_response = requests.get(image)
        with open(file_path, "wb") as file:
            file.write(image_response.content)
    else:
        image.save(file_path)
    



import sys
if __name__ == "__main__":
    k = int(sys.argv[1])
    client = AzureOpenAI(
        # add your api information here
    )
    

    while True:
        specified_skill = "color"
        skills, descriptions, categories, refined_config = load_configs_new(client, k, "./config", specified_skill)
        if specified_skill not in categories:
            import pdb; pdb.set_trace()
        sentence, questions = generate_sentence(client, skills, descriptions, json_config=refined_config)
    
