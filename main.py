import os
import network
import urequests
import time
import ubinascii
import random

from constants import INSTRUCTION
from config import OPENAI_API_KEY, OPENAI_ENDPOINT, IMGBB_API_KEY, IMGBB_ENDPOINT
from trash import trash

# Replace with your network credentials
ssid = "BND-Ueberwachungswagen2"
password = "Heute.03.12.23!"


# Connect to Wi-Fi
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    while not wlan.isconnected():
        print("Connecting to WiFi...")
        time.sleep(1)
    
    print("Connected to WiFi")
    print(wlan.ifconfig())
    
# Function to encode the image
def encode_image_in_chunks(file_path, chunk_size=128):
    encoded_parts = []
    try:
        with open(file_path, 'rb') as img_file:
            while True:
                chunk = img_file.read(chunk_size)
                if not chunk:
                    break
                encoded_chunk = ubinascii.b2a_base64(chunk).decode('utf-8').strip()
                encoded_parts.append(encoded_chunk)
                # Clear the memory for the chunk after processing
                del chunk
    except MemoryError:
        print("MemoryError: Failed to allocate memory for image chunk.")
        return None
    return ''.join(encoded_parts)

# Function to upload an image to ImgBB
def upload_image_to_imgbb(image_path):
    with open(image_path, 'rb') as img_file:
        image_data = img_file.read()
        
    payload = {
        'key': IMGBB_API_KEY,
        'image': image_data
    }
    headers = {
        'Content-Type': 'application/octet-stream'
    }
    
    response = urequests.post(IMGBB_ENDPOINT, data=payload, headers=headers)
    return response

def get_random_image():
    return trash[random.randint(0, len(trash) - 1)]
    

def get_data(model="gpt-4o", is_local_image=False, image_path=""):
    image = image_path
    if is_local_image:
        image = encode_image_in_chunks(image_path)
    else:
        if image_path:
            image = image_path
        else:
            image = get_random_image()
    data = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": [
                            {
                                "type": "text",
                                "text": INSTRUCTION,
                            }
                        ]
                },
                {
                    "role": "user",
                    "content": [
                            # {
                            # "type": "text",
                            # "text": "Here a picture of my trash"
                            # },
                            {
                            "type": "image_url",
                            "image_url": {
                                "url": image
                            }
                            }
                        ]
                },
            ],
            "max_tokens": 200
        }
    return data

# Function to send a request to OpenAI API
def get_openai_response():
    print("Sending request to OpenAI API...")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    # data = get_data(image_path="https://i0.wp.com/post.healthline.com/wp-content/uploads/2020/05/yawning_overtired_baby-1296x728-header.jpg?w=1155&h=1528")
    data = get_data(is_local_image=True, image_path="baby.png")

    response = urequests.post(OPENAI_ENDPOINT, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        print("Response from OpenAI:")
        print(result['choices'][0]['message']['content'].strip())
    else:
        print("Error:", response.status_code, response.text)

# Main function
def main():
    connect_wifi(ssid, password)
    upload_image_to_imgbb(image_path="baby.png")
    # get_openai_response()

# Run the main function
if __name__ == "__main__":
    main()