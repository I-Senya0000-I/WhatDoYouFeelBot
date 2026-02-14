import database
from typing import Optional, str


def get_reaction(receiver, chat) -> Optional[str]:
    stats = json.loads(receiver["stats"])
    history = json.loads(receiver["history"])
    return None
    

    

