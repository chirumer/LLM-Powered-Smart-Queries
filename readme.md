### sample curl (for backend):

curl -X POST -H "Content-Type: application/json" -d '{
  "query": "Tell me the mobile number of the customer with customer number 0007224787800000659700",
  "environment": "dev",
  "database": "all"
}' http://127.0.0.1:3000/query

### sample response (from backend):
{
  "cost": {
    "embedding_cost": "Rs. 0.00003",
    "model_cost": "Rs. 0.92134"
  },
  "result": "[]",
  "sql_query": "SELECT mobile FROM hyperface_dev_db.customer WHERE id = '0007224787800000659700'"
}

### cost for updating embeddings of ironbank + grimlock + jetfire:
{'embedding_cost': 'Rs. 0.05485', 'model_cost': 'Rs. 0.00000'}
