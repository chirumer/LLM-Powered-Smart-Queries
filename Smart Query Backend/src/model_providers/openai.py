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