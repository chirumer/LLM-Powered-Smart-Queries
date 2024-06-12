class Request_data:
    def __init__(self, db_conn, database, query, model):
        self.db_conn = db_conn
        self.database = database
        self.query = query
        self.model = model
        self.embedding_model = "openai | text-embedding-3-small"
        self.usage_data = {
            'embedding': 0,
            'model_input': 0,
            'model_output': 0
        }
    
    def get_usage_data(self):
        return self.usage_data.copy()