from openai import OpenAI

client = OpenAI()
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
embedding_tokens_per_dollar = 0.02/10**6
model_input_tokens_per_dollar = 3/10**6
model_output_tokens_per_dollar = 6/10**6

embedding_tokens_per_rupee = embedding_tokens_per_dollar * usd_to_inr
model_input_tokens_per_rupee = model_input_tokens_per_dollar * usd_to_inr
model_output_tokens_per_rupee = model_output_tokens_per_dollar * usd_to_inr