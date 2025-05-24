import secrets
import ccxt
#import pandas as pd
from typing import List, Optional, Dict
from pydantic import BaseModel



class Exhanage_model(BaseModel):
    name : str
    api_key : str
    secret :str

class BotArbitraggio:
    def __init__(self, exchanges_configs:List[Exhanage_model], soglia_minima:float = 0.5):
        self.exchanges = {}
        self.soglia_minima = soglia_minima
        self.inizializza_exchanges(exchanges_configs)

    def inizializza_exchanges(self, exchanges_configs)->None:

        if exchanges_configs:
            for exchange_config in exchanges_configs:
                exchange_class = getattr(ccxt, exchange_config.name)
                self.exchanges[exchange_config.name] = exchange_class(
                {
                "api" : exchange_config.api_key,
                "secrets" : exchange_config.secret
                }
                )
        #print(self.exchanges)

    def ottieni_order_books(self, symbol:str, *args)->dict:
        order_books = {}
        try:

            for exchange_name, exchange in self.exchanges.items():
                order_book = exchange.fetch_order_book(symbol)
                order_books[exchange_name] = {
                "bid" : order_book["bids"][0] if order_book["bids"] else [0,0], #comprare
                "ask" :order_book["asks"][0] if order_book["asks"] else [float("inf"), 0] #vendere

                }
        except Exception as e:
            print(str(e))

        return order_books

    def calcola_opprtunita_arbitraggio(self, order_books : Dict [str, Dict])->Optional[Dict]:
        miglior_opportunita = None
        max_profit = 0
        exchanges = list(order_books.keys())

        try:
            for buy_exchange in exchanges:
                for sell_exchange in exchanges:
                    if buy_exchange == sell_exchange:
                        continue

                    prezzo_acquisto = order_books[buy_exchange]["bid"][0]
                    prezzo_vendita = order_books[buy_exchange]["ask"][0]
                    print(prezzo_vendita, prezzo_acquisto)

                    if prezzo_acquisto > 0 and prezzo_vendita > prezzo_acquisto:
                        #calcola il percentuale di profetto  ((Pvn - Paq) /Paq) * 100
                        percentuale_profitto = ((prezzo_vendita - prezzo_acquisto) / prezzo_acquisto) * 100
                        # Considera le commissioni (assumiamo 0.1% per exchange)
                        commissioni = 0.0
                        profitto_netto = percentuale_profitto - commissioni
                        if profitto_netto>max_profit and profitto_netto > self.soglia_minima:
                            miglior_opportunita = {

                            "buy_exchange" : buy_exchange,
                            "sell_exchange" : sell_exchange,
                            "buy_price" : prezzo_acquisto,
                            "sell_price" : prezzo_vendita,
                            "profit_percentage" : profitto_netto,
                            "buy_volume" : order_books[buy_exchange]["bid"][1],
                            "sell_volume" : order_books[sell_exchange]["ask"][1]

                            }

        except Exception as e :
            print(str(e))
        return miglior_opportunita





    def check_markets(self, exchange_name:str = "binance"):
        print(self.exchanges[exchange_name].fetch_balance())


exchanges = [
Exhanage_model(**{"name" : "cryptocom", "api_key" : "x", "secret" : secrets.token_hex(32)}),
Exhanage_model(**{"name" : "binance", "api_key" : "x", "secret" : secrets.token_hex(32)}),
]
bot = BotArbitraggio(exchanges)



order_books = bot.ottieni_order_books('BTC/USD')
print(bot.calcola_opprtunita_arbitraggio(order_books))
