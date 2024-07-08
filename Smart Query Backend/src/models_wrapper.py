from openai import OpenAI
from cost_estimation_module import update_embedding_usage, update_model_input_usage, update_model_output_usage
from model_providers import openai
from model_providers import google
from model_providers import groq
from custom_exceptions import ApplicationException

client = OpenAI()
EMBEDDING_MODEL = "text-embedding-3-small"
LANGUAGE_MODEL = "gpt-3.5-turbo-instruct"


def create_embedding(data, request_data=None):
    # if request_data is None:
    #     # default to openai
    #     creator = openai.create_embedding
    # else:
    #     model_provider = request_data.embedding_model.split(' | ')[0]

    #     if model_provider == 'openai':
    #         creator = openai.create_embedding
    #     elif model_provider == 'google':
    #         creator = google.create_embedding
    #     else:
    #         raise ApplicationException(f'Unknown model provider: {model_provider}')

    # openai embeddings for now
    creator = openai.create_embedding
        
    response = creator(data)
    if (request_data is not None):
        update_embedding_usage(request_data.usage_data, response['usage'])
    return response['embedding']

def get_instruct_response(prompt, request_data):
    model_provider = request_data.model.split(' | ')[0]
    model = request_data.model.split(' | ')[1]

    if model_provider == 'openai':
        creator = openai.get_instruct_response
    elif model_provider == 'google':
        creator = google.get_instruct_response
    elif model_provider == 'groq':
        creator = groq.get_instruct_response
    else:
        raise ApplicationException(f'Unknown model provider: {model_provider}')
    
    response = creator(model, prompt)
    update_model_input_usage(request_data.usage_data, response['usage']['input'])
    update_model_output_usage(request_data.usage_data, response['usage']['output'])

    print(f'response generated: {response["response"]}')

    return response['response']