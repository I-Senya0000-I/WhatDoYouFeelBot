from groq import Groq

import json
from random import randint
import database
from typing import Optional, str


def get_persona_response(persona_name, history) -> str:
    with open(f"personas/{persona_name}.json", 'r') as file:
        persona = json.load(file)
    construct = Groq(api_key=open("./API keys/Construct API key.txt", encoding="utf-8").read().strip())
    inland_empire = Groq(api_key=open("./API keys/Inland Empire API key.txt", encoding="utf-8").read().strip())


def get_reactions(receiver, chat) -> Optional[str]:
    stats = json.loads(receiver["stats"])
    history = json.loads(chat["history"])
    for persona in stats["activation_rate"]:
        if randint(1, 100) <= round(stats["activation_rate"][persona]["chance"] * 100):
            yield get_persona_response(persona, history)
    return None
