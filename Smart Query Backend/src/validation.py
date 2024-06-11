import json
from configuration import get_database_credentials_for_environment
from text_embeddings import get_embeddings
import sqlparse
from custom_exceptions import QueryGenerationFail




### EXPORTS ###

def validate_query(query, environment, database):
    if not query:
        return { 'is_valid': False, 'reason': 'query is empty' }
    if not get_database_credentials_for_environment(environment):
        return { 'is_valid': False, 'reason': f'no credentials set for the environment: {environment}' }
    if not get_embeddings(database):
        return { 'is_valid': False, 'reason': f'unknown database selected: {database}' }    

    return { 'is_valid': True }

def is_generated_safe_query(query):
    parsed = sqlparse.parse(query)
    if len(parsed) != 1:
        return False
    statement = parsed[0]
    if statement.get_type() != 'SELECT':
        return False
    return True

def get_validated_relevant_tables(result, candidates):
    # can throw JSONDecodeError and QueryGenerationFail

    if not result:
        raise QueryGenerationFail(QueryGenerationFail.Reason.NOT_ENOUGH_CONTEXT)
    
    result = json.loads(result) 
    if not isinstance(result, list):
        raise QueryGenerationFail(QueryGenerationFail.Reason.NOT_ENOUGH_CONTEXT)

    max_confidence = 0
    for i in result:

        # check for hallucination
        if i not in candidates:
            print(f'hallucinated table found: {i}')
            raise QueryGenerationFail(QueryGenerationFail.Reason.NOT_ENOUGH_CONTEXT)
        
        if candidates[i] > max_confidence:
            max_confidence = candidates[i]
    
    print(f'confidence in tables selection: {max_confidence}')
    if max_confidence < CONSTANTS.CONFIDENCE_THRESHOLD:
        print(f'max confidence in selection too low: {max_confidence}')
        raise QueryGenerationFail(QueryGenerationFail.Reason.NOT_ENOUGH_CONTEXT)

    print('successfully found relevant tables')
    return result

### EXPORTS ###