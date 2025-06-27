import json
import requests
from config import Config
import logging
import json

def make_llm_request(prompt, model=Config.OPENROUTER_MODEL):
    try:
        headers = {
            "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        data = json.dumps({
            "model": model,
            "messages": [
              {
                "role": "user",
                "content": prompt
              }
            ],
        })
        response = requests.post(
            url=Config.OPENROUTER_URL,
            headers=headers,
            data=data
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
        result = response.json()["choices"][0]["message"]["content"]
        return result
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to make LLM request: {e}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON response: {e}")
        return None
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None
    

def llm_extract_outing_info(user_input):
    prompt = f""" 
                You are an assistant that extracts outing plans from natural language.
                    Extract and return JSON with the following structure:

                    {{
                    "city": string,
                    "state": string,
                    "drive_time_max": integer (minutes),
                    "visit_time_window": {{
                        "earliest": string (HH:MM),
                        "latest": string (HH:MM)
                    }},
                    "preferences": {{
                        "stroller_friendly": boolean,
                        "shaded": boolean,
                        "free": boolean,
                        "educational": boolean
                    }}
                    }}

                    User input:
                    "{user_input}"
                    Only respond with the above JSON, do not explain or include any new information and do not include backticks.
            """
    
    result = make_llm_request(prompt)
    if result:
        return dict(json.loads(result))
    else:
        return None

def llm_summarize_places(user_input, places):
    prompt = f""" 
                You are an assistant that summarizes a list of places based on provided user input.
                From the places data return a summary of the places that best match the user input. 
                Present the summary in natural language.
                Do not reference the places data or use the term "user" in your response.
                Return the summary in JSON format with the following structure:
                Do not use backticks or new line characters in your response
                {{"introduction": string,
                    "places_summary": [{{"name": string, 
                    "address": string, 
                    "type": string,
                    description": string,
                    "website": string,
                    "phone": string,
                    "hours": string,}}],
                    "conclusion": string                             
                }}

        
                   Places:
                    {json.dumps(places)}

                    User input:
                    "{user_input}"
            """
    result = make_llm_request(prompt)
    if result:
        return result
    else:
        return None
