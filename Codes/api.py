from flask import Flask, request
import base64
import os
import requests
import json


image_path = "/home/pumtacho/Documents/pumtacho/images/photo.jpg"
if os.path.isfile(image_path):
    print("File exists.")
else:
    print("File does not exist.")


# OpenAI API Key
api_key = "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"

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    

# Getting the base64 string
base64_image = encode_image(image_path)

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

prompt_text = (
    "Analyze the image provided and identify each visible waste item. "
    "Categorize the items based on the following rules: "
    "If the image contains multiple different types of items, categorize them collectively under Non-Recyclable Waste Bin (2). "
    "If all items are of the same type, categorize them into their appropriate bin. "
    "For uncertain or non-identifiable items, use Non-Recyclable Waste Bin (2).\n\n"
    "Respond with the bin number, followed by a colon and a space, and then list the identified items. "
    "Ensure the response always starts with the bin number. For example:\n"
    "2: Banana, Plastic Water Bottle, Paper Napkin\n"
    "1: Apple\n"
    "3: Plastic Bottle\n"
    "2: NotSure\n\n"
    "This format is crucial for the automated process that sorts the waste based on your categorization."
)

payload = {
    "model": "gpt-4-vision-preview",
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt_text},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }
    ],
    "max_tokens": 300
}

response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

response_data = response.json()
content = response_data["choices"][0]["message"]["content"]
print(content)