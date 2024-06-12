def create_embedding(data):
    pass

def get_instruct_response(prompt, usage_data):
    pass

usd_to_inr = 83.5
dollar_per_model_input_token = 0.35/10**6
dollar_per_model_output_token = 0.7/10**6

rupees_per_model_input_token = dollar_per_model_input_token * usd_to_inr
rupees_per_model_output_token = dollar_per_model_output_token * usd_to_inr