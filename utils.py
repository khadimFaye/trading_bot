from typing import List, Dict, Optional
import os, json

def get_exchanges(exchange_name: Optional[str])->List[Dict] | Dict:
    path = os.path.join(os.getcwd(), "exchanges.json")
    exchanges = []
    with open(path, "r", encoding ="utf-8") as file:
        exchanges = json.load(file)


    def search_exchange_by_name(name)->Dict:
        pass

    if exchange_name:
        return search_exchange_by_name(exchange_name)
    return exchanges  # or return a default dictionary

