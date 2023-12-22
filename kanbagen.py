import json
import time
import requests
import base64
import configparser
import argparse
import os

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

    argParser = argparse.ArgumentParser()
    argParser.add_argument("-s", "--suffix", type=str, default="", help="Common prompt suffix")
    argParser.add_argument("-o", "--output", type=str, default="output", help="Output directory")
    argParser.add_argument("-n", "--nprefix", action='store_true', help="Add numeric prefix to images")
    argParser.add_argument("-p", "--pprefix", action='store_true', help="Add prompt prefix to images")
    args = argParser.parse_args()

    print(f'Starting with arguments: {args}')

    print(f'API key: {api_key}, secret: <hidden>')

    if not os.path.exists(args.output):
        os.makedirs(args.output)

    api = Text2ImageAPI('https://api-key.fusionbrain.ai/', api_key, api_secret)
    model_id = api.get_model()
    print(f'Using model: {model_id}')

    file = open('input.txt', 'r')
    prompts = file.readlines()

    num = 1

    for prompt in prompts:
        prompt_with_suffix = prompt + " " + args.suffix
        print(f'Generating with prompt: {prompt_with_suffix}')
        uuid = api.generate(prompt_with_suffix, model_id)
        images = api.check_generation(uuid)
        img_data = bytes(images[0], "utf-8")
        filename_prefix = "image"

        if args.nprefix:
            filename_prefix = f"{num:03d}"

        if args.pprefix:
            clean_string = filter(lambda x: x.isalnum() or x.isspace(), prompt)
            filename_prefix = filename_prefix + "_" + "".join(clean_string).replace(" ", "_")
        
        filename = f"{filename_prefix}_{uuid}.jpg"

        file_path = os.path.join(args.output, filename)  

        with open(file_path, "wb") as fh:
            fh.write(base64.decodebytes(img_data))
        print(f'Saved result as {file_path}')

        num = num + 1

    print(f'Generation complete!')

