import os
import requests
import logging
from requests.exceptions import HTTPError, RequestException
import time
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

"""
This code interacts with the OpenAI GPT API.

Allows querying different models and supports JSON mode.
"""

def get_gpt_response(prompt: str, model="gpt-4o", json_mode=False, retries=3, backoff_factor=2)-> Dict[str, Any]:
    """
    Queries the OpenAI API with a specified model and prompt.
    
    Args:
        prompt (str): The prompt to send to the API.
        model (str): Model to use for the query. Defaults to 'gpt-3.5-turbo-0125'.
        response_format (dict, optional): Specifies the response format. Use {"type": "json_object"} for JSON mode.
        retries (int): Number of retries for transient errors.
        backoff_factor (int): Factor by which to multiply delay for each retry.
        
    Returns:
        dict: The API response.
        
    Raises:
        ValueError: If the OpenAI API key is not set.
        Exception: For unrecoverable errors.
    """
    api_key = os.getenv("OPENAI_API_KEY")  # Get API key from environment variable
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set in environment variables")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "response_format": "json_object" if json_mode else "text"
    }

    # if json_mode:
    #     data["type"] = "json_object"   ## FIX THIS LATER

    url = "https://api.openai.com/v1/chat/completions"

    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()  # Raises HTTPError for bad responses
            return response.json()["choices"][0]["message"]["content"]
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            if response.status_code < 500:  # Client error, no retry
                break
        except RequestException as err:
            logging.error(f'Request error occurred: {err}')
        except Exception as e:
            logging.error(f'An unexpected error occurred: {e}')
            raise
        time.sleep(backoff_factor * (2 ** attempt))
    else:
        raise Exception(f"Failed to get response after {retries} attempts.")

# Example usage
if __name__ == "__main__":
    prompt = "What is the capital of France."
    try:
        response = get_gpt_response(prompt, model="gpt-4-0125-preview", json_mode=True)
        print(response)
    except Exception as e:
        logging.error(f"Error fetching response: {e}")
