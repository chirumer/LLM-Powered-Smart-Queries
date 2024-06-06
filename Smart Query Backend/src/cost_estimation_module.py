model_input_tokens_generated = 0
model_output_tokens_generated = 0
embedding_tokens_generated = 0

def update_embedding_usage(usage):
    global embedding_tokens_generated
    embedding_tokens_generated += usage

def update_model_input_usage(usage):
    global model_input_tokens_generated
    model_input_tokens_generated += usage

def update_model_output_usage(usage):
    global model_output_tokens_generated
    model_output_tokens_generated += usage