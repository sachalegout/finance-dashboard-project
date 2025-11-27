import yfinance as yf
import pandas as pd

# Ticker choisi : NVIDIA
TICKER = "BTC-USD"

def get_historical_data(period="6mo"):
    """
    Récupère les données historiques de NVIDIA (Prix ajusté) pour une période donnée.
    Utilise une API publique (yfinance)[cite: 17].
    """
    try:
        # Récupère les données (via une API publique - Core Feature 16)
        data = yf.download(TICKER, period=period, interval="1d", progress=False)

        if 'Adj Close' in data.columns:
            data = data.rename(columns={'Adj Close': 'Price'})
        elif 'Close' in data.columns:
            data = data.rename(columns={'Close': 'Price'})

        return data[['Price']].dropna()
    except Exception as e:
        # Gestion d'erreur (Robustness) [cite: 60]
        print(f"Erreur lors de la récupération des données historiques: {e}")
        return pd.DataFrame()

def get_realtime_price():
    """
    Récupère le prix actuel de NVIDIA pour l'affichage en temps réel[cite: 6].
    """
    try:
        ticker_obj = yf.Ticker(TICKER)
        info = ticker_obj.info
        # Cherche le prix actuel ou le prix du marché régulier
        current_price = info.get('currentPrice') or info.get('regularMarketPrice')

        if current_price:
            return f"{current_price:,.2f}"
        else:
            return "N/A"

    except Exception as e:
        # Gestion d'erreur (Robustness) [cite: 60]
        print(f"Erreur lors de la récupération du prix actuel: {e}")
        return "N/A"

if __name__ == '__main__':
    # Test du module
    historical_df = get_historical_data(period="3mo")
    print(f"--- Données Historiques de {TICKER} ---")
    print(historical_df.head())

    current_price = get_realtime_price()
    print(f"\nPrix actuel de {TICKER}: ${current_price}")