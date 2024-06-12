from openai import OpenAI
import os

API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=API_KEY)
EMBEDDING_MODEL = "text-embedding-3-small"
LANGUAGE_MODEL = "gpt-3.5-turbo-instruct"


def create_embedding(data):
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=[data])
    embedding = [e.embedding for e in response.data][0]
    return {
        'embedding': embedding,
        'usage': response.usage.total_tokens
    }

def get_instruct_response(prompt):
    response = client.completions.create(
        model=LANGUAGE_MODEL,
        prompt=prompt,
        max_tokens=150
    )
    model_response = response.choices[0].text.strip()

    return {
        'response': model_response,
        'usage': {
            'input': response.usage.prompt_tokens,
            'output': response.usage.completion_tokens
        }
    }

usd_to_inr = 83.5
dollar_per_embedding_token = 0.02/10**6
dollar_per_model_input_token = 1.5/10**6
dollar_per_model_output_token = 2/10**6

rupees_per_embedding_token = dollar_per_embedding_token * usd_to_inr
rupees_per_model_input_token = dollar_per_model_input_token * usd_to_inr
rupees_per_model_output_token = dollar_per_model_output_token * usd_to_inr