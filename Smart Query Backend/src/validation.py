from configuration import get_database_credentials_for_environment
from text_embeddings import get_embeddings


def validate_query(query, environment, database):
    if not query:
        return { 'is_valid': False, 'reason': 'query is empty' }
    if not get_database_credentials_for_environment(environment):
        return { 'is_valid': False, 'reason': f'no Credentials set for the environment: {environment}' }
    if not get_embeddings(database):
        return { 'is_valid': False, 'reason': f'unknown database selected: {database}' }    

    return { 'is_valid': True }