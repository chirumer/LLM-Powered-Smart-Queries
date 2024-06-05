from openai import OpenAI


client = OpenAI()
EMBEDDING_MODEL = "text-embedding-3-small"


def create_embedding(data):
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=[data])
    embedding = [e.embedding for e in response.data][0]
    return embedding

def get_instruct_response(prompt):
    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=150
    )
    return response