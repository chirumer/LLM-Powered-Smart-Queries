import os
import google.generativeai as genai

API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')


def create_embedding(data):
    pass

def get_instruct_response(prompt):
    print('using gemini')
    response = model.generate_content(prompt)

    return {
        'response': response.text,
        'usage': {
            'input': response.usage_metadata.prompt_token_count,
            'output': response.usage_metadata.candidates_token_count,
        }
    }

usd_to_inr = 83.5
dollar_per_model_input_token = 0.35/10**6
dollar_per_model_output_token = 0.7/10**6

rupees_per_model_input_token = dollar_per_model_input_token * usd_to_inr
rupees_per_model_output_token = dollar_per_model_output_token * usd_to_inr