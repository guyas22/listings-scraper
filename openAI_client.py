from openai import OpenAI
import json
import numpy as np
import os

class OpenAIClient:
    def __init__(self, logger):
        self.logger = logger
        try:
            if os.getenv("STAGE") == "local":
                self.logger.info("Initializing OpenAI client in local stage.")
                openai_api_key = os.getenv("OPENAI_API_KEY")
            elif os.getenv("STAGE") == "prod":
                self.logger.info("Initializing OpenAI client in production stage.")
                secret_string = os.getenv("MY_SECRET")
                secrets = json.loads(secret_string)
                openai_api_key = secrets['OPENAI_API_KEY']
            else:
                raise ValueError("Unknown STAGE environment variable. It must be either 'local' or 'prod'.")

            # Initialize the OpenAI client
            self.client = OpenAI(api_key=openai_api_key)
            self.logger.info("OpenAI client initialized successfully")

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse secrets from MY_SECRET: {e}")
            raise
        except KeyError as e:
            self.logger.error(f"Missing expected key in secrets or environment: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI Client: {e}")
            raise

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
            self.logger.info(f"OpenAI response: {response}")
            self.logger.info(f"Content: {content}")
            self.logger.info("Transforming to JSON")
            
            # Convert the string response to a JSON object
            json_response = self._parse_json_content(content)
        except Exception as e:
            self.logger.error(f"Error during OpenAI API call: {e}")
            json_response = self._default_json_response()
        
        self.logger.info(f"JSON response: {json_response}")
        self.logger.info(f"Type of JSON response: {type(json_response)}")
        return json_response

    def _parse_json_content(self, content):
        try:
            json_response = json.loads(content)
            return self._clean_json_response(json_response)
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing JSON: {e} with content: {content}")
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
