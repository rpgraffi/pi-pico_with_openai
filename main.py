import os
import network
import urequests
import time
import ubinascii
import random
import ujson
import re

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
    


def get_random_image():
    return trash[random.randint(0, len(trash) - 1)]
    

def get_data(model="gpt-4o", is_local_image=False, image_path=""):
    image = image_path
    if is_local_image:
        print("Upload currenlty not supported")
        # image = encode_image_in_chunks(image_path)
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
    # data = get_data(is_local_image=True, image_path="baby.png")
    data = get_data()

    response = urequests.post(OPENAI_ENDPOINT, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        result_json = result['choices'][0]['message']['content'].strip()
        print("Response from OpenAI:")
        print(result['choices'][0]['message']['content'].strip())
        sort_trash(result_json)
    else:
        print("Error:", response.status_code, response.text)
        
def sort_trash(json):
    # Remove backticks from the response
    cleaned_response = re.sub(r'json', '', json).strip().strip('')
    cleaned_response = re.sub(r'`', '', cleaned_response).strip().strip('')

    # Parse the cleaned JSON response
    data = ujson.loads(cleaned_response)

    # Get the category from the parsed data
    category = data['selectedBin'][0]['category']

    # Dictionary to simulate switch case
    switch_case = {
        "blue": lambda: print(data['selectedBin'][0]['explanation'] + "\nCategory is Blue bin (blaue Tonne): For paper and cardboard. You cannot use plastic bags for the blue bin. Flatten cardboard boxes before you recycle them."),
        "yellow": lambda: print(data['selectedBin'][0]['explanation'] + "\nCategory is Yellow or orange bin (Wertstofftonne): For plastic and metal containers, and containers with the Gruener Punkt logo."),
        "brown": lambda: print(data['selectedBin'][0]['explanation'] + "\nCategory is Brown bin (Biomuell): For biodegradable goods. It's used to make biogas and compost. Don't use plastic or biodegradable bags, only paper bags."),
        "grey": lambda: print(data['selectedBin'][0]['explanation'] + "\nCategory is Grey bin (Restmuell): Things that you cannot sell, donate, or recycle."),
        "glass": lambda: print(data['selectedBin'][0]['explanation'] + "\nCategory is Glass recycling bins (Glasiglus): For glass containers that don't have a deposit (Pfand). In Berlin, you don't need to clean glass containers. If your building does not have glass recycling bins, find them in your neighborhood. There are 3 bin types: Braunglas bin for brown glass, Gruenglas bin for green, red, and blue glass, Weissglas bin for transparent glass."),
        "problem": lambda: print(data['selectedBin'][0]['explanation'] + "\nCategory is Problematic: For everything that is not meant to be thrown away."),
        "none": lambda: print(data['selectedBin'][0]['explanation'] + "\nCategory is Not recognized: If not recognized, the image returns this."),
    }

    # Default action if category is not found
    default_action = lambda: print("Category not recognized. Most likely OpenAI gave an invalid formatted json response.")

    # Execute the corresponding action or the default action
    switch_case.get(category, default_action)()
    return category

# Main function
def main():
    connect_wifi(ssid, password)
    get_openai_response()

# Run the main function
if __name__ == "__main__":
    main()