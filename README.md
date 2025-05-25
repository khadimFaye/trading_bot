🤖 Crypto Trading Bot
Un bot di trading automatico per criptovalute costruito con Python e CCXT che implementa strategie di trading algoritmico su exchange multipli.
🚀 Caratteristiche

Multi-Exchange Support: Compatibile con Binance, Kraken, Bitfinex e altri
Strategie Multiple: Grid Trading, DCA, Arbitraggio, Mean Reversion
Risk Management: Stop Loss automatici, Position Sizing, Risk Limits
Real-time Monitoring: Dashboard live con metriche di performance
Backtesting: Test delle strategie su dati storici
Notifiche: Alert via Telegram/Discord per trades e alert importanti

📋 Prerequisiti
bashPython 3.8+
pip install ccxt pandas numpy ta-lib requests python-telegram-bot
⚙️ Installazione
bash# Clone del repository
git clone https://github.com/khadimFaye/trading_bot 

cd crypto-trading-bot

# Installazione dipendenze
pip install -r requirements.txt

# Configurazione
cp config.example.py config.py
# Modifica config.py con le tue API keys
🔧 Configurazione
1. API Keys Exchange
python# config.py
EXCHANGE_CONFIG = {
    'binance': {
        'apiKey': 'your_binance_api_key',
        'secret': 'your_binance_secret',
        'sandbox': True,  # True per testnet
        'enableRateLimit': True,
    }
}

🎯 Strategie Disponibili
Grid Trading
Piazza ordini buy/sell a intervalli regolari per profittare dalla volatilità:

bash# ```python main.py -s 0.5```

il flag -s server per specificare la soglia minima


