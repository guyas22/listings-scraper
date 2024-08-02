from openai import OpenAI
client = OpenAI()

def parse_img_to_json(base64_image):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
            "role": "system",
            "content": [
                {
                "type": "text",
                "text": "you are a real - estate agent looking for details in listings. your job is to get a json file with the important details out of the image"
                }
            ]
            },
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": "return a json file format of the important information in the image"
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
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
    
    print(f"OpenAI response: {response}")
    return response