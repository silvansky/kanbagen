import json
import time
import requests
import base64
import configparser

class Text2ImageAPI:

    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_model(self):
        response = requests.get(self.URL + 'key/api/v1/models', headers=self.AUTH_HEADERS)
        data = response.json()
        print(f'Available models: {data}')
        return data[0]['id']

    def generate(self, prompt, model, images=1, width=1024, height=1024):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": f"{prompt}"
            }
        }

        data = {
            'model_id': (None, model),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/text2image/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        return data['uuid']

    def check_generation(self, request_id, attempts=10, delay=10):
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/text2image/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['images']

            attempts -= 1
            time.sleep(delay)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    api_key = config['API']['key']
    api_secret = config['API']['secret']

    print(f'Starting with API key: {api_key}, secret: <hidden>')

    api = Text2ImageAPI('https://api-key.fusionbrain.ai/', api_key, api_secret)
    model_id = api.get_model()
    print(f'Using model: {model_id}')

    # Using readlines()
    file = open('input.txt', 'r')
    prompts = file.readlines()

    for prompt in prompts:
        print(f'Generating with prompt: {prompt}')
        uuid = api.generate(prompt, model_id)
        images = api.check_generation(uuid)
        img_data = bytes(images[0], "utf-8")
        filename = f"image_{uuid}.jpg" 
        with open(filename, "wb") as fh:
            fh.write(base64.decodebytes(img_data))
        print(f'Saved result as {filename}')

    print(f'Generation complete!')

