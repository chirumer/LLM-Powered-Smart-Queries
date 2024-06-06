from openai import OpenAI
from cost_estimation_module import update_embedding_usage, update_model_input_usage, update_model_output_usage

client = OpenAI()
EMBEDDING_MODEL = "text-embedding-3-small"
LANGUAGE_MODEL = "gpt-3.5-turbo-instruct"


def create_embedding(data):
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=[data])
    update_embedding_usage(response.usage.total_tokens)
    embedding = [e.embedding for e in response.data][0]
    return embedding

def get_instruct_response(prompt):
    response = client.completions.create(
        model=LANGUAGE_MODEL,
        prompt=prompt,
        max_tokens=150
    )
    update_model_input_usage(response.usage.prompt_tokens)
    update_model_output_usage(response.usage.completion_tokens)

    print(response)

    return response.choices[0].text.strip()