# openAI_client.py
from openai import OpenAI
import json
client = OpenAI()

def parse_img_to_json(base64_image):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {
            "role": "system",
            "content": [
                {
                "type": "text",
                "text": "you are an AI RE assistant.Your job is to extract specific information from real estate listing images"
                }
            ]
            },
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": "extract details from image in json:Furnished(Yes/No),Parking(Yes/No),Bedrooms(num),Asking Rent(num),price per square feet(num) If any missing or needs to be guessed return 'NA'"
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
