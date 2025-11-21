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

def calculate_ma_crossover(prices: pd.Series, short_window: int = 50, long_window: int = 200) -> pd.Series:
    """
    Stratégie des Moyennes Mobiles Croisées : Achat lorsque la MA courte > MA longue.
    """
    # Nécessite au moins la longue fenêtre de données pour démarrer
    if prices.empty or len(prices) < long_window:
        if not prices.empty:
             return pd.Series([100.0], index=[prices.index[-1]])
        else:
             return pd.Series(dtype=float)

    # CORRECTION : prices.values.ravel() pour garantir que l'array est 1D
    prices_df = pd.DataFrame({'Price': prices.values.ravel()}, index=prices.index)
    
    # Calcul des Moyennes Mobiles
    prices_df['Short_MA'] = prices_df['Price'].rolling(window=short_window).mean()
    prices_df['Long_MA'] = prices_df['Price'].rolling(window=long_window).mean()
    
    # Génération du signal : 1.0 (Achat/Long) si MA courte > MA longue, 0.0 sinon.
    prices_df['Signal'] = 0.0
    prices_df['Signal'][short_window:] = np.where(prices_df['Short_MA'][short_window:] > prices_df['Long_MA'][short_window:], 1.0, 0.0)
    
    # Détermination des positions : 1 (Achat), -1 (Vente), 0 (Conservation/Cash)
    prices_df['Position'] = prices_df['Signal'].diff()
    prices_df['Position'].iloc[0] = prices_df['Signal'].iloc[0] # Position initiale
    
    # Calcul des rendements quotidiens de l'actif
    prices_df['Market_Returns'] = prices_df['Price'].pct_change()
    
    # Rendements de la stratégie : Rendement du marché * Position de la veille
    prices_df['Strategy_Returns'] = prices_df['Signal'].shift(1).fillna(0) * prices_df['Market_Returns']
    
    # Valeur cumulée du portefeuille (Base 100)
    cumulative_value = (1 + prices_df['Strategy_Returns']).cumprod()
    
    # Normalisation : Démarrer la stratégie après la période d'initialisation de la MA longue
    start_index = prices_df['Long_MA'].first_valid_index()
    if start_index in cumulative_value.index and not cumulative_value[start_index] == 0:
        cumulative_value = cumulative_value / cumulative_value[start_index] * 100.0
    else:
        # Si la normalisation à l'index de départ échoue, normaliser à partir du premier jour valide
        cumulative_value = cumulative_value / cumulative_value.dropna().iloc[0] * 100.0
    
    return cumulative_value

def calculate_metrics(returns: pd.Series, risk_free_rate=0.04) -> dict:
    """
    Calcule les métriques de performance clés (Max-Drawdown et Sharpe Ratio).
    """
    if returns.empty or len(returns) < 2:
        return {"Max Drawdown": "N/A", "Sharpe Ratio (Annuel)": "N/A"}
        
    # Rendements quotidiens
    daily_returns = returns.pct_change().dropna()

    # 1. Max Drawdown (Glissement Maximum)
    cumulative_returns = (1 + daily_returns).cumprod()
    rolling_max = cumulative_returns.cummax()
    drawdown = (cumulative_returns / rolling_max) - 1
    
    # Utilisation de .item() pour extraire le scalaire (correction de TypeError)
    max_drawdown = drawdown.min().item() 
    
    # 2. Sharpe Ratio Annuel
    annualization_factor = np.sqrt(252)
    
    # Utilisation de .item() pour extraire le scalaire (correction de TypeError)
    avg_return = daily_returns.mean().item() * 252 # Annualisé
    volatility = daily_returns.std().item() * annualization_factor # Annualisé
    
    # Conversion en float pour la comparaison
    volatility = float(volatility) 
    
    # Sharpe Ratio
    if volatility == 0:
        sharpe_ratio = 0.0
    else:
        sharpe_ratio = float((avg_return - risk_free_rate) / volatility)
        
    return {
        "Max Drawdown": f"{max_drawdown * 100:.2f} %", 
        "Sharpe Ratio (Annuel)": f"{sharpe_ratio:.2f}"
    }


def run_backtest(data: pd.DataFrame, strategy_name: str, **params) -> pd.Series:
    """
    Exécute la stratégie demandée sur les données de prix.
    """
    prices = data['Price']
    
    if strategy_name == "Buy-and-Hold":
        # CORRECTION APPLIQUÉE
        return calculate_buy_and_hold(prices)
    
    elif strategy_name == "MA Crossover":
        # Récupère les paramètres passés par Streamlit
        short_window = params.get('short_window', 50)
        long_window = params.get('long_window', 200)
        return calculate_ma_crossover(prices, short_window, long_window)
    
    return pd.Series(dtype=float)


if __name__ == '__main__':
    # --- Test du module (simuler des données) ---
    dates = pd.date_range(start='2024-01-01', periods=250)
    data_test = pd.DataFrame({
        'Price': np.random.normal(loc=100, scale=1, size=250).cumsum() + 100
    }, index=dates)

    bh_results = run_backtest(data_test, "Buy-and-Hold")
    ma_results = run_backtest(data_test, "MA Crossover", short_window=20, long_window=50)

    print("--- Résultat Buy-and-Hold (Base 100) ---")
    print(bh_results.tail(3))
    print(f"Métriques B&H: {calculate_metrics(bh_results)}")
    
    print("\n--- Résultat MA Crossover (Base 100) ---")
    print(ma_results.tail(3))
    print(f"Métriques MA: {calculate_metrics(ma_results)}")