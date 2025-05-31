from arbitraggio import BotArbitraggio, Exhanage_configuration
from utils import get_exchanges
import argparse
import sys
from typing import List, Dict

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Bot Arbitraggio')
    parser.add_argument('-e', help='Specifica l\'exchange da utilizzare', required=False, )
    parser.add_argument('-d', help='Default', required=False,  action="store_true")
    parser.add_argument('-s', "--soglia_minima", help='impostare soglia minima ', required=True, type=float)
    if len(sys.argv) == 1:
        print("Utilizzo corretto e python main.py < flag > [Options]\n \nesempio dei flag da usare : \n -d [ per caricare tutti gli exchange automaticamente ] \n -e [ per specificare l'exchange da utilizzare ]")
        sys.exit(1)

    args = parser.parse_args()
    if args.e:
        exchanges = get_exchanges(args.e) #usa l'exchange specificato
        if not exchanges:
           print(f"[ {args.e} ] non trovato controlla se non ci sono errori di digitura")

    else:
        exchanges : List[Dict] = get_exchanges() #ottieni tutti gli exchanges 

    if exchanges:
        exchange_configs : List[Exhanage_configuration] = [Exhanage_configuration(**exchange) for exchange in exchanges if type(exchange) ==dict] if isinstance(exchanges, list) else [Exhanage_configuration(**exchanges)]
        print(exchanges)
        bot = BotArbitraggio (exchange_configs, args.soglia_minima)
        bot.monitora_opportunita_arbitraggio(["BTC/USD"])
        
    
   