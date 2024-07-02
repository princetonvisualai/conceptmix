import json
import argparse
import sys
sys.path.append('./')
from t2v_metrics.t2v_metrics import VQAScore, CLIPScore, ITMScore
from dynamix.grading.gpt_grading import gpt_grading, gpt_grading_azure, gpt_grading_azure_two
import os


def write_json_data(file, data, is_first_element):
    """Writes a single JSON object to the file with proper formatting."""
    json_string = json.dumps(data, indent=4)
    if not is_first_element:
        file.write(",\n")
    else:
        is_first_element = False
    file.write(json_string)
    return is_first_element

def main(args):
    image_question_path = args.image_question_path
    score_path = args.score_path
    model_name = args.model_name
    logprobs = args.logprobs
    print("Score path: ", score_path)
    os.makedirs(os.path.dirname(score_path), exist_ok=True)

    with open(image_question_path) as file:
        data = json.load(file)

    score_data = []
    dataset = []

    # Handle scoring for GPT model
    if model_name == 'gpt':
        with open(score_path, "w") as f:
            f.write("[]")

        with open(score_path, "r+") as file:
            file.seek(0, os.SEEK_END)
            file.seek(file.tell() - 1, os.SEEK_SET)  
            is_first_element = (file.tell() == 1)  

            total_all_correct = 0
            total_score = 0
            total_questions = 0  
            for item in data:
                score_item = {
                    'image_path': item['image_path'],
                    'questions': [],
                    'scores': []
                }
                all_questions_correct = True 
                item_total_score = 0
                for question in item['question']:
                    if not question.strip(): 
                        continue
                    try:
                        response = gpt_grading_azure(logprobs, item['image_path'], item['prompt'], question)
                        # response = gpt_grading(item['image_path'], item['prompt'], question)
                        score_item['questions'].append(question)
                        score_item['scores'].append(response)
                        item_total_score += response
                        total_questions += 1  
                        if response == 0:
                            all_questions_correct = False
                            print("turning 0 because of ", question, response)
                    except:
                        print("Error in response")
                
                total_score += item_total_score
                is_first_element = write_json_data(file, score_item, is_first_element)
                total_all_correct += all_questions_correct
            
            proportion_all_correct = total_all_correct / len(data)
            average_score_per_image = total_score / total_questions  
            print(proportion_all_correct)

            summary_data = {
                "proportion_all_correct": proportion_all_correct,
                "average_score_per_image": average_score_per_image
            }
            if not is_first_element:
                file.write(",\n")
            json.dump(summary_data, file)
            file.write("\n]")

    else:
        raise NotImplementedError



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate VQA and CLIP scores for generated images.')
    parser.add_argument('--image_question_path', type=str, help='Path to the JSON file containing the results.')
    parser.add_argument('--score_path', type=str,
                        help='Path to the JSON file to save the scores.')
    parser.add_argument('--model_name', type=str, default='gpt', help='Name of the model to use for scoring.')
    parser.add_argument('--logprobs', type=str, default=False, help='Whether to calculate logprobs for GPT.')
    args = parser.parse_args()
    main(args)


