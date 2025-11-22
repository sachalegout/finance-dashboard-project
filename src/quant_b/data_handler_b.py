# src/quant_b/data_handler_b.py
import yfinance as yf
import pandas as pd
from .config import TICKERS_B

def get_historical_data_multi(period="1y"):
    """
    Récupère les prix ajustés historiques pour tous les tickers du portefeuille.
    """
    try:
        data = yf.download(TICKERS_B, period=period, interval="1d", progress=False)

        if 'Adj Close' in data.columns:
            prices = data['Adj Close'].dropna(how='all')
        elif 'Close' in data.columns:
            prices = data['Close'].dropna(how='all')
        else:
            print("Erreur : Colonne 'Adj Close' ou 'Close' introuvable.")
            return pd.DataFrame()

        # Nettoyage pour les cas spéciaux d'un seul ticker
        if isinstance(prices, pd.Series):
             prices = prices.to_frame(TICKERS_B[0])
        
        return prices
    except Exception as e:
        print(f"Erreur lors de la récupération des données multi-actifs : {e}")
        return pd.DataFrame()

def get_realtime_prices_multi():
    """
    Récupère le prix actuel pour chaque actif du portefeuille.
    """
    prices = {}
    for ticker in TICKERS_B:
        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info
            price = info.get('currentPrice') or info.get('regularMarketPrice')
            prices[ticker] = f"{price:,.2f}" if price else "N/A"
        except Exception:
            prices[ticker] = "N/A"
    return prices

if __name__ == '__main__':
    historical_df = get_historical_data_multi(period="6mo")
    print(f"--- Données Multi-Actifs pour {TICKERS_B} ---")
    print(historical_df.head())
    
    current_prices = get_realtime_prices_multi()
    print(f"\nPrix actuels : {current_prices}")