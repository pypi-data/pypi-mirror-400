import argparse
import configparser
import os
import sys
from pathlib import Path

from openai import OpenAI

CONFIG_DIR = Path.home() / '.config' / 'watcmd'
CONFIG_FILE = CONFIG_DIR / 'config.ini'

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "anthropic/claude-sonnet-4.5"


def get_api_key():
    if CONFIG_FILE.exists():
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        return config['DEFAULT']['api_key']
    return os.environ.get('OPENROUTER_API_KEY')

def setup_config(api_key):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config = configparser.ConfigParser()
    config['DEFAULT'] = {'api_key': api_key}
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)
    print(f"API key saved to {CONFIG_FILE}")


def query_llm(prompt):
    api_key = get_api_key()
    if not api_key:
        print("Error: OpenRouter API key not found. Please set it using 'watcmd --setup YOUR_API_KEY'")
        sys.exit(1)

    client = OpenAI(api_key=api_key, base_url=OPENROUTER_BASE_URL)

    try:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are a silent assistant that just outputs UNIX cli commands"},
                {"role": "user", "content": "what command for listing all files"},
                {"role": "assistant", "content": "ls -a"},
                {"role": "user", "content": f"what command {prompt}"}
            ],
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error: API request failed. {str(e)}")
        sys.exit(1)



def main():
    parser = argparse.ArgumentParser(description="Get UNIX commands from text explanations using AI")
    parser.add_argument('--setup', metavar='API_KEY', help='Setup OpenRouter API key')
    parser.add_argument('query', nargs='*', help='The task description to get a UNIX command for')
    args = parser.parse_args()

    if args.setup:
        setup_config(args.setup)
        print("API key set successfully.")
    elif args.query:
        query = ' '.join(args.query)
        suggested_command = query_llm(query)
        print(suggested_command)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()