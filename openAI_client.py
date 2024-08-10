# openAI_client.py
from openai import OpenAI
import json
import numpy as np
client = OpenAI()


def parse_img_to_json(base64_image):
    SYSTEM_PROMPT="you are an AI RE assistant.Your job is to extract specific information from real estate listing images"
    MESSAGE_PROMPT="extract details from image in json (strict names):Furnished(Yes/No),Parking(Yes/No),price per square feet(INT) If any missing or needs to be guessed return 'NA'"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {
            "role": "system",
            "content": [
                {
                "type": "text",
                "text": SYSTEM_PROMPT
                }
            ]
            },
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": MESSAGE_PROMPT
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}",
                    "detail": "high"
                }
                }
            ]
            }
        ],
        temperature=1,
        max_tokens=1692,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )
    content = response.choices[0].message.content
    print(f"OpenAI response: {response}")
    print(f"Content: {content}")
    print("transforming to JSON")
    # Convert the string response to a JSON object
    try:
        json_response = json.loads(content)
        json_response = clean_json_response(json_response)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e} with content: {content}")
        json_response = {
            "Furnished": "NA",
            "Parking": "NA",
            "Bedrooms": "NA",
            "Asking Rent": "NA",
            "Price per square feet": "NA"
        }
    print(f"JSON response: {json_response}")
    print(f"typeof JSON response: {type(json_response)}")
    return json_response


def clean_json_response(json_response):
    # Replace non-JSON-compliant float values with 0 or any other appropriate value
    for key, value in json_response.items():
        if isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
            json_response[key] = "NA"
    return json_response