import os
import requests


def get_rupees_per_model_input_token(model):
    # to update
    return 0

def get_rupees_per_model_output_token(model):
    # to update
    return 0

def get_instruct_response(model_selected, prompt):
    url = "http://localhost:8080/completion"
    headers = {"Content-Type": "application/json"}
    payload = {
        "prompt": prompt,
        "n_predict": 128
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        return {
            'response': data['content'],
            'usage': {
                'input': data['tokens_evaluated'],
                'output': data['tokens_predicted'],
            }
        }
    else:
        raise Exception(f"Request failed with status code {response.status_code}")