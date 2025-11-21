import pandas as pd
import numpy as np

def calculate_buy_and_hold(prices: pd.Series) -> pd.Series:
    """
    Calcule la performance cumulée de la stratégie Buy-and-Hold (base 100).
    """
    if prices.empty:
        return pd.Series(dtype=float)
        
    # Rendements quotidiens
    returns = prices.pct_change().fillna(0)
    
    # Performance cumulée (valeur du portefeuille, base 100)
    cumulative_value = (1 + returns).cumprod()
    
    # Normalise pour commencer à 100.0
    cumulative_value = cumulative_value / cumulative_value.iloc[0] * 100.0
    
    return cumulative_value

def calculate_metrics(returns: pd.Series, risk_free_rate=0.04) -> dict:
    """
    Calcule les mÃ©triques de performance clÃ©s (Max-Drawdown et Sharpe Ratio).
    """
    if returns.empty or len(returns) < 2:
        return {"Max Drawdown": "N/A", "Sharpe Ratio (Annuel)": "N/A"}
        
    # Rendements quotidiens
    daily_returns = returns.pct_change().dropna()

    # 1. Max Drawdown (Glissement Maximum)
    # Calcule la performance cumulÃ©e (base 1)
    cumulative_returns = (1 + daily_returns).cumprod()
    
    # Calcule les pics prÃ©cÃ©dents
    rolling_max = cumulative_returns.cummax()
    
    # Calcule le glissement
    drawdown = (cumulative_returns / rolling_max) - 1
    max_drawdown = drawdown.min()
    
    # 2. Sharpe Ratio Annuel
    # Assumons 252 jours de trading par an
    annualization_factor = np.sqrt(252)
    
    # Rendement moyen et volatilitÃ©
    avg_return = daily_returns.mean() * 252 # AnnualisÃ©
    volatility = daily_returns.std() * annualization_factor # AnnualisÃ©
    
    # Sharpe Ratio
    if volatility == 0:
        sharpe_ratio = 0
    else:
        sharpe_ratio = (avg_return - risk_free_rate) / volatility
        
    return {
        "Max Drawdown": f"{max_drawdown * 100:.2f} %",
        "Sharpe Ratio (Annuel)": f"{sharpe_ratio:.2f}"
    }


def run_backtest(data: pd.DataFrame, strategy_name: str) -> pd.Series:
    """
    ExÃ©cute la stratÃ©gie demandÃ©e sur les donnÃ©es de prix.
    """
    prices = data['Price']
    
    if strategy_name == "Buy-and-Hold":
        return calculate_buy_and_hold(prices)
    
    # Ajoutez ici la prochaine stratÃ©gie (ex: Momentum)
    
    return pd.Series(dtype=float)


if __name__ == '__main__':
    # --- Test du module (simuler des donnÃ©es) ---
    dates = pd.date_range(start='2024-01-01', periods=10)
    data_test = pd.DataFrame({
        'Price': [100, 101, 99, 105, 100, 110, 120, 115, 130, 140]
    }, index=dates)

    bh_results = run_backtest(data_test, "Buy-and-Hold")
    
    print("--- RÃ©sultat Buy-and-Hold (Base 100) ---")
    print(bh_results)
    
    # Test des mÃ©triques sur les rendements
    metrics = calculate_metrics(bh_results)
    print("\n--- MÃ©triques de Performance ---")
    print(metrics)