from scipy import spatial
from text_embeddings import create_embedding, get_embeddings
from database_connection import DatabaseConnection
import json
from models_wrapper import get_instruct_response

def get_top_N_related_tables(query, N=8):
    query_embed = create_embedding(query)
    relatedness_fn = lambda x, y: 1 - spatial.distance.cosine(x, y)

    embeds = get_embeddings()

    score = []
    for table, embedding in embeds.items():
        score.append((table, relatedness_fn(query_embed, embedding)))

    score.sort(key=lambda x: x[1], reverse=True)
    return score[:N]

def generate_selection_prompt(candidates, query):
    db_conn = DatabaseConnection()
    
    prompt = 'Here are the tables available:\n'
    for table, _ in candidates:
        schema = db_conn.describe_table(*table.split('.'))
        fields = [column[0] for column in schema]
        prompt += f'{table}: {", ".join(fields)}\n'

    prompt += "Please find which tables are relevant to solve queries. You must answer ONLY a valid json array and NOTHING ELSE.\n\n"
    prompt += f"Query: In the {table.split('.')[1]} table of {table.split('.')[0]} database, is the {schema[0][0]} column a primary key?\n"
    prompt += f"Relevant Tables: [\"{table}\"]\n"
    prompt += f"Query: In the {table.split('.')[1]} table of {table.split('.')[0]} database, Are there multiple values of {schema[0][0]} which are same?\n"
    prompt += f"Relevant Tables: [\"{table}\"]\n"
    prompt += f"Query: {query}\n"
    prompt += f"Relevant Tables: "
    return prompt

def select_relevant_tables(query):
    candidates = get_top_N_related_tables(query)
    prompt = generate_selection_prompt(candidates, query)

    invalid_output_count = 0
    while invalid_output_count < 3:
        try:
            response = get_instruct_response(prompt)
            result = response.choices[0].text.strip()
            print(result)
            result = json.loads(result)
            print('success')
            return result

        except json.JSONDecodeError:
            invalid_output_count += 1

    raise Exception("Invalid output from model 3 times")