#  Licensed under the MIT license.

import configparser
import argparse
import logging
import asyncio
import random
import os

from .model import download_model_folder, download_reverse_model_folder, load_model
from .decoder import generate_response

path = os.path.dirname(os.path.abspath(__file__))
# Script arguments can include path of the config
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--config', type=str, default=os.path.join(path, "chatbot.cfg"))
args = arg_parser.parse_args()

# Read the config
config = configparser.ConfigParser(allow_no_value=True)
with open(args.config) as f:
    config.read_file(f)

# Download and load main model
target_folder_name = download_model_folder(config)
model, tokenizer = load_model(target_folder_name, config)

# Download and load reverse model
use_mmi = config.getboolean('model', 'use_mmi')
if use_mmi:
    mmi_target_folder_name = download_reverse_model_folder(config)
    mmi_model, mmi_tokenizer = load_model(mmi_target_folder_name, config)
else:
    mmi_model = None
    mmi_tokenizer = None
 
USERS = {
    "turns": {}
}

get = lambda history: generate_response(model, tokenizer, history, config, mmi_model=mmi_model, mmi_tokenizer=mmi_tokenizer)[0]


async def get_response(user_id, prompt):
    # Parse parameters
    max_turns_history = 5 

    turns = USERS["turns"].get(user_id)
    if turns is None:
        USERS["turns"][user_id] = []
        turns = USERS["turns"][user_id] 
 
    if prompt.lower() == 'bye' or prompt.lower() == 'quit':
        USERS["turns"][user_id] = []
        return "EXIT" 
        
    # A single turn is a group of user messages and bot responses right after
    turn = {
        'user_messages': [],
        'bot_messages': []
    }
    turns.append(turn)
    turn['user_messages'].append(prompt)
    # Merge turns into a single history (don't forget EOS token)
    history = ""
    from_index = max(len(turns)-max_turns_history-1, 0) if max_turns_history >= 0 else 0
    for turn in turns[from_index:]:
        # Each turn begings with user messages
        for message in turn['user_messages']:
            history += message + tokenizer.eos_token
        for message in turn['bot_messages']:
            history += message + tokenizer.eos_token

    # Generate bot messages
    loop = asyncio.get_running_loop() 
    bot_message = await loop.run_in_executor(None, get, history) 
    turn['bot_messages'].append(bot_message)
    return bot_message
