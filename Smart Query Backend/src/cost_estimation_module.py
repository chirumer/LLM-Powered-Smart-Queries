from model_providers import openai
from model_providers import google
from custom_exceptions import ApplicationException

### exports

def update_embedding_usage(usage_data, usage):
    if usage:
        usage_data['embedding'] += usage

def update_model_input_usage(usage_data, usage):
    if usage:
        usage_data['model_input'] += usage

def update_model_output_usage(usage_data, usage):
    if usage:
        usage_data['model_output'] += usage

###


def convert_embedding_usage_to_cost(model, usage):
    model_provider = model.split(' | ')[0]

    if model_provider == 'openai':
        embedding_tokens_per_rupee = openai.embedding_tokens_per_rupee
    elif model_provider == 'google':
        embedding_tokens_per_rupee = google.embedding_tokens_per_rupee
    else:
        raise ApplicationException(f'Unknown model provider: {model_provider}')

    return usage * embedding_tokens_per_rupee

def convert_model_input_usage_to_cost(model, usage):
    model_provider = model.split(' | ')[0]

    if model_provider == 'openai':
        model_input_tokens_per_rupee = openai.model_input_tokens_per_rupee
    elif model_provider == 'google':
        model_input_tokens_per_rupee = google.model_input_tokens_per_rupee
    else:
        raise ApplicationException(f'Unknown model provider: {model_provider}')

    return usage * model_input_tokens_per_rupee

def convert_model_output_usage_to_cost(model, usage):
    model_provider = model.split(' | ')[0]

    if model_provider == 'openai':
        model_output_tokens_per_rupee = openai.model_output_tokens_per_rupee
    elif model_provider == 'google':
        model_output_tokens_per_rupee = google.model_output_tokens_per_rupee
    else:
        raise ApplicationException(f'Unknown model provider: {model_provider}')

    return usage * model_output_tokens_per_rupee

def convert_model_usage_to_cost(model, model_input_usage, model_output_usage):
    return convert_model_input_usage_to_cost(model, model_input_usage) + convert_model_output_usage_to_cost(model, model_output_usage)


### exports

def calculate_cost(request_data, checkpoint_before):

    checkpoint_after = request_data.usage_data

    embedding_tokens_generated = checkpoint_after['embedding'] - checkpoint_before['embedding']
    model_input_tokens_generated = checkpoint_after['model_input'] - checkpoint_before['model_input']
    model_output_tokens_generated = checkpoint_after['model_output'] - checkpoint_before['model_output']

    def format_cost(cost):
        return f"Rs. {cost:.5f}"

    embedding_cost = convert_embedding_usage_to_cost(request_data.embedding_model, embedding_tokens_generated)
    model_cost = convert_model_usage_to_cost(request_data.model, model_input_tokens_generated, model_output_tokens_generated)
    
    return {
        'embedding_cost': format_cost(embedding_cost),
        'model_cost': format_cost(model_cost),
        'total_cost': format_cost(embedding_cost + model_cost)
    }

###