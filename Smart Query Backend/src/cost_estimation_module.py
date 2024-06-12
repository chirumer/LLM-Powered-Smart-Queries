model_input_tokens_generated = 0
model_output_tokens_generated = 0
embedding_tokens_generated = 0

### exports

def update_embedding_usage(usage_data, usage):
    global embedding_tokens_generated
    if usage:
        embedding_tokens_generated += usage
        usage_data['embedding'] += usage

def update_model_input_usage(usage_data, usage):
    global model_input_tokens_generated
    if usage:
        model_input_tokens_generated += usage
        usage_data['model_input'] += usage

def update_model_output_usage(usage_data, usage):
    global model_output_tokens_generated
    if usage:
        model_output_tokens_generated += usage
        usage_data['model_output'] += usage

###


usd_to_inr = 83.5
embedding_tokens_per_dollar = 0.02/10**6
model_input_tokens_per_dollar = 3/10**6
model_output_tokens_per_dollar = 6/10**6

embedding_tokens_per_rupee = embedding_tokens_per_dollar * usd_to_inr
model_input_tokens_per_rupee = model_input_tokens_per_dollar * usd_to_inr
model_output_tokens_per_rupee = model_output_tokens_per_dollar * usd_to_inr

def convert_embedding_usage_to_cost(usage):
    return usage * embedding_tokens_per_rupee

def convert_model_input_usage_to_cost(usage):
    return usage * model_input_tokens_per_rupee

def convert_model_output_usage_to_cost(usage):
    return usage * model_output_tokens_per_rupee

def convert_model_usage_to_cost(model_input_usage, model_output_usage):
    return convert_model_input_usage_to_cost(model_input_usage) + convert_model_output_usage_to_cost(model_output_usage)


### exports

def get_usage_checkpoint():
    return {
        'embedding': embedding_tokens_generated,
        'model_input': model_input_tokens_generated,
        'model_output': model_output_tokens_generated
    }

def calculate_cost(checkpoint_before, checkpoint_after):

    embedding_tokens_generated = checkpoint_after['embedding'] - checkpoint_before['embedding']
    model_input_tokens_generated = checkpoint_after['model_input'] - checkpoint_before['model_input']
    model_output_tokens_generated = checkpoint_after['model_output'] - checkpoint_before['model_output']

    def format_cost(cost):
        return f"Rs. {cost:.5f}"

    embedding_cost = convert_embedding_usage_to_cost(embedding_tokens_generated)
    model_cost = convert_model_usage_to_cost(model_input_tokens_generated, model_output_tokens_generated)
    
    return {
        'embedding_cost': format_cost(embedding_cost),
        'model_cost': format_cost(model_cost),
        'total_cost': format_cost(embedding_cost + model_cost)
    }

###