import requests
import json

def synthesize_speech(text, output_path, seed, url="http://localhost:8000/tts"):
    # Define the payload for the POST request
    payload = {
        "text": text,
        "output_path": output_path,
        "seed": seed
    }
    
    # Define the headers for the POST request
    headers = {
        "content-type": "application/json"
    }
    
    try:
        # Make the POST request to the FastAPI TTS endpoint
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        # Check if the request was successful
        if response.status_code == 200:
            print(f"Speech synthesis succeeded. Output saved to {output_path}.")
        else:
            print(f"Failed to synthesize speech. Status code: {response.status_code}")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
synthesize_speech("朋友你好啊，今天天气怎么样 ？", "output.wav", 232)

