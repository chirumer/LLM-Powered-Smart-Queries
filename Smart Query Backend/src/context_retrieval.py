from scipy import spatial
from text_embeddings import create_embedding, get_embeddings
from database_connection import DatabaseConnection
import json
from models_wrapper import get_instruct_response
from custom_exceptions import ApplicationException, QueryGenerationFail
from configuration import CONSTANTS

def get_top_N_related_tables(database, query, N=8):
    query_embed = create_embedding(query)
    relatedness_fn = lambda x, y: 1 - spatial.distance.cosine(x, y)

    embeds = get_embeddings(database)

    score_dict = {}
    for table, embedding in embeds.items():
        score_dict[table] = relatedness_fn(query_embed, embedding)

    sorted_score_dict = dict(sorted(score_dict.items(), key=lambda item: item[1], reverse=True)[:N])
    return sorted_score_dict

def generate_selection_prompt(db_conn, candidates, query):
    
    prompt = 'Here are the tables available:\n'
    for table in candidates:
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

def select_relevant_tables(db_conn, database, query):
    candidates = get_top_N_related_tables(database, query)
    prompt = generate_selection_prompt(db_conn, candidates, query)

    invalid_output_count = 0
    while invalid_output_count < CONSTANTS.MAX_RELEVANT_TABLE_REGENERATION:
        try:
            result = get_instruct_response(prompt)
            print(result)
            result = json.loads(result)

            # none selected
            if not result:
                print('no tables selected')
                raise QueryGenerationFail(QueryGenerationFail.Reason.NOT_ENOUGH_CONTEXT)

            for i in result:

                # check for hallucination
                if i not in candidates:
                    print(f'hallucinated table found: {i}')
                    raise QueryGenerationFail(QueryGenerationFail.Reason.NOT_ENOUGH_CONTEXT)
                
                # check for low confidence
                max_confidence = 0
                for i in result:
                    if candidates[i] > max_confidence:
                        max_confidence = candidates[i]
                print(f'confidence in tables selection: {max_confidence}')
                if max_confidence < CONSTANTS.CONFIDENCE_THRESHOLD:
                    print(f'max confidence in selection too low: {max_confidence}')
                    raise QueryGenerationFail(QueryGenerationFail.Reason.NOT_ENOUGH_CONTEXT)

            print('successfully found relevant tables')
            return result

        except json.JSONDecodeError:
            invalid_output_count += 1

    raise ApplicationException("JSON decoding relevant tables kept failing")