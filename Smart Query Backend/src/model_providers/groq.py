import os
from groq import Groq

API_KEY = os.getenv('GROQ_API_KEY')
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)


def get_instruct_response(model_selected, prompt):
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an instruction following AI model which does exactly as told and only that.",
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=model_selected,
    )

    return {
        'response': response.choices[0].message.content,
        'usage': {
            'input': response.usage.prompt_tokens,
            'output': response.usage.completion_tokens,
        }
    }


def get_rupees_per_model_input_token(model):
    # to update

    return 0

def get_rupees_per_model_output_token(model):
    # to update

    return 0