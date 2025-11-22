import yfinance as yf
import pandas as pd
import numpy as np
import datetime as dt
import os 

# --- CONFIGURATION ---
TICKER = "NVDA"
# Le rapport sera stockÃ© dans un dossier 'data'
REPORT_FILE = "data/daily_report_NVDA.txt"

def calculate_max_drawdown(prices: pd.Series) -> float:
    """Calcule le glissement maximum (Max Drawdown)."""
    cumulative_returns = prices.pct_change().dropna().add(1).cumprod()
    rolling_max = cumulative_returns.cummax()
    drawdown = (cumulative_returns / rolling_max) - 1
    # Retourne le scalaire
    return drawdown.min().item()

def generate_report():
    """RÃ©cupÃ¨re les donnÃ©es, calcule les mÃ©triques et gÃ©nÃ¨re le contenu du rapport."""
    
    # RÃ©cupÃ©rer les donnÃ©es sur 6 mois pour la volatilitÃ© et le drawdown
    end_date = dt.datetime.now()
    start_date = end_date - dt.timedelta(days=180)
    
    try:
        data = yf.download(TICKER, start=start_date, end=end_date, progress=False)
        
        if data.empty:
            return f"--- Rapport Quotidien {TICKER} ({dt.date.today()}) ---\nERREUR: Aucune donnÃ©e rÃ©cupÃ©rÃ©e.\n"

        # 1. MÃ©triques sur la pÃ©riode (6 mois)
        daily_returns = data['Close'].pct_change().dropna()
        annualization_factor = np.sqrt(252)
        
        annual_volatility = daily_returns.std().item() * annualization_factor
        max_drawdown = calculate_max_drawdown(data['Close'])

        # 2. DonnÃ©es du dernier jour de trading
        last_day = data.iloc[-1]
        
        date_report = last_day.name.strftime('%Y-%m-%d')
        # CORRECTION : Utilisation de .item() pour obtenir des floats scalaires
        open_price = last_day['Open'].item() 
        close_price = last_day['Close'].item()
        
        daily_return = (close_price / open_price) - 1
        
        # 3. GÃ©nÃ©ration du contenu
        report_content = f"--- Rapport Quotidien {TICKER} du {date_report} ---\n"
        report_content += f"GÃ©nÃ©rÃ© le : {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report_content += "\n"
        report_content += "--- DonnÃ©es ClÃ©s (Dernier Jour de Trading) ---\n"
        report_content += f"Prix d'Ouverture : {open_price:.2f} $\n"
        report_content += f"Prix de ClÃ´ture : {close_price:.2f} $\n"
        report_content += f"Performance journaliÃ¨re : {daily_return * 100:.2f} %\n"
        report_content += "\n"
        report_content += "--- MÃ©triques de Risque (6 Derniers Mois) ---\n"
        report_content += f"VolatilitÃ© AnnualisÃ©e : {annual_volatility * 100:.2f} %\n"
        report_content += f"Max Drawdown : {max_drawdown * 100:.2f} %\n"
        
        return report_content

    except Exception as e:
        return f"--- Rapport Quotidien {TICKER} ({dt.date.today()}) ---\nERREUR lors de la rÃ©cupÃ©ration des donnÃ©es : {e}\n"

if __name__ == "__main__":
    # CrÃ©e le dossier 'data' s'il n'existe pas
    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    
    report = generate_report()
    
    # Ã‰criture du rapport
    with open(REPORT_FILE, "w") as f:
        f.write(report)
    
    print(f"Rapport quotidien gÃ©nÃ©rÃ© avec succÃ¨s dans {REPORT_FILE}")