import openai
import json
import re
from visonorm.global_variables import OPENAI_MODEL, MAX_TOKENS, TEMPERATURE

def run_chatgpt(nsw, openai_api_key, prompt):
    openai.api_key = openai_api_key
    # Generate text using the ChatGPT 'completions' API with the new syntax
    response = openai.chat.completions.create(
            model=OPENAI_MODEL,  # or use "gpt-4" if you have access to it
            messages=[{"role": "user", "content": prompt}],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE
        )

    # Get the generated text from the response
    response_dict = response.model_dump()    # <--- convert to dictionary
    response_message = response_dict["choices"][0]["message"]["content"]
    response_str = response_message

    return response_str



