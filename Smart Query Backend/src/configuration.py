from enum import Enum
import os
from dotenv import load_dotenv
from database_connection import DatabaseCredentials
from custom_exceptions import ApplicationException
from enum import Enum


class CONSTANTS(Enum):
    MAX_QUERY_REGENERATION = 3
    MAX_RELEVANT_TABLE_REGENERATION = 3


def load_credentials():
    credentials = {}

    ### temporary
    load_dotenv(dotenv_path='.env')
    db_host = os.getenv('DB_HOST')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_credentials = DatabaseCredentials(db_host, db_user, db_password)
    credentials['dev'] = db_credentials
    ###

    return credentials

credentials = load_credentials()


def get_database_credentials_for_environment(environment):
    if environment in credentials:
        return credentials[environment]
    
def get_all_database_credentials():
    db_credentials = []
    for i in credentials:
        db_credentials.append(credentials[i])
    return db_credentials


def filter_databases(databases):

    ### temporary
    accepted_databases = ['grimlock_dev_db', 'hyperface_dev_db', 'hyperface_platform_dev']
    databases = [db for db in databases if db in accepted_databases]
    ###

    return databases

def filter_tables(database, tables):

    ### temporary
    if database == 'hyperface_platform_dev':
        accepted_tables = ['job', 'job_type_config', 'shedlock']
        tables = [table for table in tables if table in accepted_tables]
    ###

    return tables