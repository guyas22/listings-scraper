from openai import OpenAI
import json
import numpy as np

class OpenAIClient:
    def __init__(self):
        self.client = OpenAI()
        print("OpenAI client initialized")

    def parse_img_to_json(self, base64_image):
        SYSTEM_PROMPT = "You are an AI RE assistant. Your job is to extract specific information from real estate listing images."
        MESSAGE_PROMPT = "Extract details from image in JSON (strict names): Furnished(Yes/No), Parking(Yes/No), price per square feet(INT). If any missing or needs to be guessed, return 'NA'."
        
        try:
            response = self.client.chat.completions.create(
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
            print("Transforming to JSON")
            
            # Convert the string response to a JSON object
            json_response = self._parse_json_content(content)
        except Exception as e:
            print(f"Error during OpenAI API call: {e}")
            json_response = self._default_json_response()
        
        print(f"JSON response: {json_response}")
        print(f"Type of JSON response: {type(json_response)}")
        return json_response

    def _parse_json_content(self, content):
        try:
            json_response = json.loads(content)
            return self._clean_json_response(json_response)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e} with content: {content}")
            return self._default_json_response()

    def _clean_json_response(self, json_response):
        # Replace non-JSON-compliant float values with "NA"
        for key, value in json_response.items():
            if isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
                json_response[key] = "NA"
        return json_response

    def _default_json_response(self):
        return {
            "Furnished": "NA",
            "Parking": "NA",
            "Bedrooms": "NA",
            "Asking Rent": "NA",
            "Price per square feet": "NA"
        }
