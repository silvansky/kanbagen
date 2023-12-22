# Setup

- Get your key and secret here: https://fusionbrain.ai/keys/
- Set your API key and secret in `config.ini`
- Run `pip install -r requirements.txt`

`config.ini` example:
```
[API]
key = keywithoutquotes
secret = secretwithoutquotes
```

# Usage

# Basic

- Write your prompts to `input.txt` line by line
- Run `python kanbagen.py`
- All generated images are in `output/`

## Available options

- `-n` to add prompt number to filename
- `-p` to add prompt to filename
- `-o <dir>` to set output directory (defaults to `output`)
- `-s <suffix>` to add custom suffix to all prompts, for example `-s "in surrealistic style"`
