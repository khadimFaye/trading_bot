import secrets
import ccxt
#import pandas as pd
from typing import List, Optional, Dict, Union, Tuple
from pydantic import BaseModel





class Exhanage_configuration(BaseModel):
    name : str
    api_key: str| None = None
    secret: str | None = None
    fees: float  | None = None

class Commissione_CCXT:

    @staticmethod
    def get_commissioni(exchange:ccxt.Exchange, symbol, *args):
        markets = exchange.load_markets()
        if symbol is not None:
            for market in markets:
                if symbol in markets:
                    market = markets[symbol]
                    if "taker" in market and "maker" in market:
                        taker: Union[float, int] = market["taker"] * 100 if market["taker"] else 0
                        #maker : Union[float, int]  = market["taker"] * 100 if market["taker"] else 0
                        print("TAKER" , market["taker"])
                        return taker #per l'atrbitraggio usare sempre taker


class BotArbitraggio:
    def __init__(self, exchanges_configs:List[Exhanage_configuration], soglia_minima:float = 0.1):
        self.exchanges = {} #
        self.soglia_minima = soglia_minima
        self.inizializza_exchanges(exchanges_configs)

    def inizializza_exchanges(self, exchanges_configs)->None:

        if exchanges_configs:
            for exchange_config in exchanges_configs:
                exchange_class = getattr(ccxt, exchange_config.name)
                self.exchanges[exchange_config.name] = exchange_class(
                {
                "apiKey" : exchange_config.api_key,
                "secret" : secrets.token_hex(32),
                "enableRateLimit" : True,
                "fess" : exchange_config.fees

                }
                )
        else:
            print(" ****** Nessuna configurazione di exchange fornita ******")
            import sys
            sys.exit(1)  # <-> ( 1 ) <-> ( 3 )  386db2b95feb92c895bcf6f5048d030cfc61c9a4


    def ottieni_order_books(self, symbol:str, *args)->dict:
        order_books = {}
        try:

            for exchange_name, exchange in self.exchanges.items():
                order_book = exchange.fetch_order_book(symbol)
                order_books[exchange_name] = {
                "bid" : order_book["bids"][0] if order_book["bids"] else [0,0], #vendere
                "ask" :order_book["asks"][0] if order_book["asks"] else [float("inf"), 0],#acquistare
               "symbol" : symbol

                }
        except Exception as e:
            print(str(e))
        return order_books

    def verifica_prezzi(self, ricavo, costo):
        if ricavo - costo >0:
            return ricavo, costo
        elif costo - ricavo >0:
            return costo , ricavo

        else:
            return 0,0
    def verifica_opportunita(self, pa : Union[int, float], pv : Union[int, float], commissioni:Dict, buy_exchange:str, sell_exchange:str, *args)->tuple[float, float,Union[int,float],  bool]:

        """ verfica se l'opportunita e profittevole o no
        ARGS :
            pa : prezzo acquisto
            pv : prezzo vendita
        commissioni : dizionario con le commissioni di acquisto e vendita
        exchange : nome dell'exchange

        RETURN :
            tuple di due float rappresentanti il profitto e il costo totale e il percentuale profitto
            bool che indica se l'opportunita e profittevole o no

        """


        buy_fees = commissioni[buy_exchange]
        sell_fess = commissioni[sell_exchange]
        costo_reale : float = pa *  (1+buy_fees) if buy_fees else 0 # pa * (1+fees)
        ricavo_reale : float = pv * (1-sell_fess) if sell_fess else 0# pa * (1+fees)

        profitto = ricavo_reale - costo_reale



        print("percentuake , ", profitto)
        profitto_pct : Union[float,int] = (profitto / costo_reale)  * 100 if costo_reale > 0 else 0

        if profitto_pct>self.soglia_minima:
            return (costo_reale, ricavo_reale, profitto, True)

        return (0.0, 0.0, 0.0, False)




    def calcola_opprtunita_arbitraggio(self, order_books : Dict [str, Dict])->Optional[Dict] | None:
        miglior_opportunita = None
        max_profit = 0
        exchanges = list(order_books.keys())
        commissioni = {}

        for exchange in exchanges:
            symbol = order_books[exchange]["symbol"]
            commissioni[exchange] = Commissione_CCXT.get_commissioni(self.exchanges[exchange], symbol)
            if commissioni[exchange] == None:
                exchanges.remove(exchange)
                commissioni.pop(exchange)
                print(exchange, "none rimosso")

        try:
            for buy_exchange in exchanges:
                for sell_exchange in exchanges:
                    if buy_exchange == sell_exchange:
                        continue

                    symbol = order_books[buy_exchange]["symbol"]

                    prezzo_acquisto = order_books[buy_exchange]["ask"][0]
                    prezzo_vendita = order_books[sell_exchange]["bid"][0]
                    print(prezzo_acquisto, "prezzi", prezzo_vendita)

                    is_opportunita =self.verifica_opportunita(pv = prezzo_vendita, pa = prezzo_acquisto, sell_exchange= sell_exchange, buy_exchange = buy_exchange, commissioni = commissioni)
                    print(is_opportunita, "dettagli")
                    if is_opportunita[-1]:
                            print("opportunita trovata")


                            miglior_opportunita = {

                            "buy_exchange" : buy_exchange,
                            "sell_exchange" : sell_exchange,
                            "buy_price" : is_opportunita[0],
                            "sell_price" : is_opportunita[1],
                            "profit_percentage" : is_opportunita[2],
                            "buy_volume" : order_books[buy_exchange]["ask"][1],
                            "sell_volume" : order_books[sell_exchange]["bid"][1],
                            "symbol": symbol

                            }
                    else:
                        is_opportunita =self.verifica_opportunita(pv = prezzo_acquisto, pa = prezzo_vendita, sell_exchange= buy_exchange, buy_exchange = sell_exchange, commissioni = commissioni)
                        if is_opportunita[-1]:

                            new_buy_exchange, new_sell_exchange = (sell_exchange, buy_exchange)
                            miglior_opportunita = {

                            "buy_exchange" : new_buy_exchange,
                            "sell_exchange" : new_sell_exchange,
                            "buy_price" : is_opportunita[0],
                            "sell_price" : is_opportunita[1],
                            "profit_percentage" : is_opportunita[2],
                            "buy_volume" : order_books[buy_exchange]["ask"][1],
                            "sell_volume" : order_books[sell_exchange]["bid"][1],
                            "symbol": symbol

                            }




        except Exception as e :
            print(str(e), "fiila")

        if miglior_opportunita:
            print("opportinita trovataaaa")
            return miglior_opportunita
        else:
            print("nessun opportunita trovata")
            return None

    def esegui_arbitraggio(self, opportunita: Dict, quantita : float, *args)->bool | None:
        import colorama
        colorama.init()

        try:
            if opportunita:

                print(colorama.Fore.GREEN +"---------------------------")
                print(colorama.Fore.GREEN +f"hai comprato {opportunita['symbol']} da {self.exchanges[opportunita['buy_exchange']]} per {self.exchanges[opportunita['buy_price']]}")
                print("")
                print(colorama.Fore.YELLOW +f"hai venduto {opportunita['symbol']} da {self.exchanges[opportunita['sell_exchange']]} per {self.exchanges[opportunita['buy_price']]}")
                print(colorama.Fore.YELLOW +"---------------------------")
            #buy_order = self.exchanges[opportunita["buy_exchange"]].create_market_buy_order(
            #symbol = opportunita["symbol"],
            #amount=quantita
            #)

            #sell_order = self.exchanges[opportunita["sell_exchange"]].create_market_buy_order(
            #symbol = opportunita["symbol"],
            #amount=quantita
            #)
        except Exception as e:
            print(str(e), "errore")

    def monitora_opportunita_arbitraggio(self, symbols : List[str], interval:float = 0.5)->bool:
        simbols = symbols
        opportunita = None
        i = 0

        while True:

            for symbol in symbols:
                order_books = self.ottieni_order_books(symbol)
                opportunita = self.calcola_opprtunita_arbitraggio(order_books)
                if opportunita:
                    opportunita["symbol"] = symbol
                    print(opportunita)
                    return self.esegui_arbitraggio(opportunita, 5)
                i+=1
                print(f"ricerca opportunita incorso .... Nr. {i}\r",flush=True, end='')





if __name__ == "__main__":
   print(__file__)




exchanges = [
Exhanage_configuration(**{"name" : "cryptocom", "api_key" : "x", "secret" : secrets.token_hex(32)}),
Exhanage_configuration(**{"name" : "binance", "api_key" : "x", "secret" : secrets.token_hex(32)}),
]

#bot = BotArbitraggio(exchanges)
#order_books = bot.ottieni_order_books('BTC/USD')
#print(bot.monitora_opportunita_arbitraggio(['BTC/USD', 'LTC/USDT']))
