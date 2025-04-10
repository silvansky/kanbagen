import json
import time
import requests
import base64
import configparser
import argparse
import os
from colorama import Fore, Back, Style

class Text2ImageAPIError(Exception):
    def __init__(self, message):
        super().__init__(message)

class Text2ImageAPI:

    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def check_availability(self, model):
        print(f'🔍 Checking availability for model {model}...')
        response = requests.get(self.URL + 'key/api/v1/pipeline/' + str(model) + '/availability', headers=self.AUTH_HEADERS)
        data = response.json()
        print(f'🔍 Response: {data}')
        
        # Try pipeline_status first, fall back to status
        status = data.get('pipeline_status', data.get('status'))
        if not status:
            print(f'❌ No status field found in response: {data}')
            raise Text2ImageAPIError(f"Invalid response format: no status field")
        
        if status != 'ACTIVE':
            print(f'❌ Model not available, status: {status}')
            raise Text2ImageAPIError(f"Model not available: {status}")
        print(f'✅ Model is available')

    def get_model(self):
        print(f'🔍 Getting available models...')
        response = requests.get(self.URL + 'key/api/v1/pipelines', headers=self.AUTH_HEADERS)
        print(f'🔍 Response: {response}')
        data = response.json()
        print(f'📋 Available models: {data}')
        model_id = data[0]['id']
        print(f'✅ Selected model: {model_id}')
        return model_id

    def generate(self, prompt, model, images=1, width=1024, height=1024):
        print(f'🎨 Generating image...')
        print(f'📝 Prompt: {prompt}')
        print(f'🔧 Parameters: {images} images, {width}x{height}')
        
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": prompt
            }
        }
        print(f'📦 Request params: {params}')

        data = {
            'pipeline_id': (None, model),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/pipeline/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        uuid = data['uuid']
        print(f'✅ Generation started, UUID: {uuid}')
        return uuid

    def check_generation(self, request_id, attempts=60, delay=20):
        print(f'🔍 Checking generation status for {request_id}...')
        last_data = "{}"
        attempt = 0

        while attempt <= attempts:
            try:
                response = requests.get(self.URL + 'key/api/v1/pipeline/status/' + request_id, headers=self.AUTH_HEADERS)
                data = response.json()
                httpStatus = response.status_code

                if httpStatus != 200:
                    print(f'❌ Bad HTTP status: {httpStatus}')
                    raise Text2ImageAPIError(f"Bad HTTP status code: {httpStatus}, data: {data}")

                status = data['status']
                print(f'📊 Generation status: {status}')

                if status == 'DONE':
                    if data['result'].get('censored', False):
                        print(f'🚫 Generation censored')
                        raise Text2ImageAPIError(f"Generation censored")

                    files = data['result']['files']
                    if not files or not isinstance(files, list):
                        print(f'❌ Invalid response format')
                        raise Text2ImageAPIError(f"Unexpected response from server")

                    img_data = files[0].encode('utf-8')
                    print(f'✅ Generation complete')
                    return img_data
                elif status == 'FAIL':
                    print(f'❌ Generation failed')
                    raise Text2ImageAPIError(f"Generation failed: {data}")

                last_data = data
            except Text2ImageAPIError:
                raise
            except Exception as e:
                print(f"\n❌ Network error: " + Fore.RED + f"{e}" + Style.RESET_ALL)

            attempt += 1
            print(f"\r⏳ Waiting for {delay} seconds, attempt {attempt}/{attempts}", end='', flush=True)
            time.sleep(delay)

        print(f'❌ Generation timed out')
        raise Text2ImageAPIError(f"Failed! Last server response: {last_data}")


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
    argParser.add_argument("-r", "--repeat", type=int, default=1, help="Repeat all generations X times. Must be greater than 0")
    argParser.add_argument("--style", type=str, default="", help="Specify style")
    args = argParser.parse_args()

    print(f'Starting with arguments: {args}')

    print(f'API key: {api_key}, secret: <hidden>')

    try:
        if not os.path.exists(args.output):
            os.makedirs(args.output)

        api = Text2ImageAPI('https://api-key.fusionbrain.ai/', api_key, api_secret)
        model_id = api.get_model()
        print(f'Using model: {model_id}')
        api.check_availability(model_id)

        file = open('input.txt', 'r')
        prompts = file.read().splitlines()
    except Exception as e:
        print(f"❌ Fatal Error: " + Fore.RED + f"{e}" + Style.RESET_ALL)
        exit(1)

    if args.repeat < 1:
        print(f"❌ Fatal Error: Repeat count must be greater than 0")
        exit(1)

    prompts = prompts * args.repeat

    num = 0
    num_prompts = len(prompts)
    successfull_generations = 0

    for prompt in prompts:
        num += 1
        prompt_with_suffix = prompt + " " + args.suffix

        print(f'Generating with prompt ' + Fore.GREEN + f'{num}/{num_prompts}' + Style.RESET_ALL + f': {prompt_with_suffix}')

        try:
            uuid = api.generate(prompt_with_suffix, model_id)
            img_data = api.check_generation(uuid)

            filename_prefix = "image"

            if args.nprefix:
                filename_prefix = f"{num:03d}"

            if args.pprefix:
                clean_string = filter(lambda x: x.isalnum() or x.isspace(), prompt_with_suffix)
                filename_prefix = filename_prefix + "_" + "".join(clean_string).replace(" ", "_")

            filename = f"{filename_prefix}_{uuid}.jpg"

            file_path = os.path.join(args.output, filename)

            with open(file_path, "wb") as fh:
                fh.write(base64.decodebytes(img_data))

            print(f'\n✅ Saved result as {file_path}')
            successfull_generations += 1
        except KeyboardInterrupt:
            print(f"\n❌ Generation aborted by user")
            break
        except Exception as e:
            print(f"\n❌ Generation failed for prompt: {prompt_with_suffix} - " + Fore.RED + f"{e}" + Style.RESET_ALL)
            continue

    print(f'Generation complete for ' + Fore.GREEN + f'{successfull_generations}/{num_prompts}' + Style.RESET_ALL + ' prompts!')

