# src/quant_a/strategy_engine.py
import pandas as pd
import numpy as np

def calculate_buy_and_hold(prices: pd.Series) -> pd.Series:
    """
    Calcule la performance cumulée de la stratégie Buy-and-Hold (Achat et Conservation).
    La série de résultats est normalisée pour commencer à 100.

    :param prices: pd.Series des prix de l'actif.
    :return: pd.Series de la valeur cumulée du portefeuille (Base 100).
    """
    if prices.empty:
        return pd.Series(dtype=float)
        
    # Rendements quotidiens
    returns = prices.pct_change().fillna(0)
    
    # Performance cumulée (valeur du portefeuille)
    cumulative_value = (1 + returns).cumprod()
    
    # Normalise pour commencer à 100.0
    cumulative_value = cumulative_value / cumulative_value.iloc[0] * 100.0
    
    return cumulative_value

def calculate_ma_crossover(prices: pd.Series, short_window: int = 50, long_window: int = 200) -> pd.Series:
    """
    Implémente la Stratégie des Moyennes Mobiles Croisées.
    Achat/Position Longue (1.0) lorsque la MA courte > MA longue.
    
    :param prices: pd.Series des prix de l'actif.
    :param short_window: Fenêtre de la Moyenne Mobile Courte (jours).
    :param long_window: Fenêtre de la Moyenne Mobile Longue (jours).
    :return: pd.Series de la valeur cumulée du portefeuille de la stratégie (Base 100).
    """
    if prices.empty or len(prices) < long_window:
        if not prices.empty:
            # Retourne une série avec une seule valeur de 100 si pas assez de données pour la MA longue
            return pd.Series([100.0], index=[prices.index[-1]])
        else:
            return pd.Series(dtype=float)

    # Assure que 'prices' est un DataFrame pour le calcul des MAs
    prices_df = pd.DataFrame({'Price': prices.values.ravel()}, index=prices.index)
    
    # Calcul des Moyennes Mobiles
    prices_df['Short_MA'] = prices_df['Price'].rolling(window=short_window).mean()
    prices_df['Long_MA'] = prices_df['Price'].rolling(window=long_window).mean()
    
    # Signal : 1.0 (Achat/Long) si MA courte > MA longue, 0.0 sinon.
    prices_df['Signal'] = 0.0
    prices_df['Signal'][long_window:] = np.where(prices_df['Short_MA'][long_window:] > prices_df['Long_MA'][long_window:], 1.0, 0.0)
    
    prices_df['Market_Returns'] = prices_df['Price'].pct_change()
    
    # Rendements de la stratégie : Rendement du marché * Position de la veille (Signal.shift(1))
    prices_df['Strategy_Returns'] = prices_df['Signal'].shift(1).fillna(0) * prices_df['Market_Returns']
    
    # Valeur cumulée du portefeuille (1 + rendement cumulé)
    cumulative_value = (1 + prices_df['Strategy_Returns']).cumprod()
    
    # Normalisation : Démarrer la stratégie après la période d'initialisation
    # Utilise l'index valide (après la MA longue) pour la normalisation à 100.0
    start_index = prices_df['Long_MA'].first_valid_index()
    if start_index in cumulative_value.index and not cumulative_value[start_index] == 0:
        cumulative_value = cumulative_value / cumulative_value[start_index] * 100.0
    else:
        # Fallback si le premier index valide est introuvable ou nul (devrait être rare)
        cumulative_value = cumulative_value / cumulative_value.dropna().iloc[0] * 100.0
    
    return cumulative_value

def calculate_metrics(returns: pd.Series, risk_free_rate=0.04) -> dict:
    """
    Calcule les métriques de performance clés : Max-Drawdown et Sharpe Ratio.

    :param returns: pd.Series de la valeur cumulée du portefeuille de la stratégie.
    :param risk_free_rate: Taux sans risque annuel (par défaut 4% ou 0.04).
    :return: dict contenant le Max Drawdown et le Sharpe Ratio annuel.
    """
    if returns.empty or len(returns) < 2:
        return {"Max Drawdown": "N/A", "Sharpe Ratio (Annuel)": "N/A"}
        
    # Rendements quotidiens (basés sur la Série de Valeur Cumulée)
    daily_returns = returns.pct_change().dropna()

    # 1. Max Drawdown
    cumulative_returns = (1 + daily_returns).cumprod()
    rolling_max = cumulative_returns.cummax()
    drawdown = (cumulative_returns / rolling_max) - 1
    max_drawdown = drawdown.min().item() 
    
    # 2. Sharpe Ratio Annuel
    annualization_factor = np.sqrt(252) # Facteur d'annualisation pour les jours de trading
    
    # Calcul de la moyenne des rendements annualisée
    avg_return = daily_returns.mean().item() * 252
    # Calcul de la volatilité annualisée (Écart-type)
    volatility = daily_returns.std().item() * annualization_factor
    
    volatility = float(volatility) 
    
    # Calcul du Sharpe Ratio
    if volatility == 0:
        sharpe_ratio = 0.0
    else:
        # Formule du Sharpe Ratio: (Rendement annuel - Taux sans risque) / Volatilité annuelle
        sharpe_ratio = float((avg_return - risk_free_rate) / volatility)
        
    return {
        "Max Drawdown": f"{max_drawdown * 100:.2f} %", 
        "Sharpe Ratio (Annuel)": f"{sharpe_ratio:.2f}"
    }


def run_backtest(data: pd.DataFrame, strategy_name: str, **params) -> pd.Series:
    """
    Fonction principale pour exécuter la stratégie demandée.

    :param data: pd.DataFrame contenant les données de prix historiques (colonne 'Price').
    :param strategy_name: Nom de la stratégie ('Buy-and-Hold' ou 'MA Crossover').
    :param params: Paramètres spécifiques à la stratégie (ex: short_window, long_window).
    :return: pd.Series de la valeur cumulée du portefeuille.
    """
    prices = data['Price']
    
    if strategy_name == "Buy-and-Hold":
        # Implémente la stratégie Buy-and-Hold
        return calculate_buy_and_hold(prices)
    
    elif strategy_name == "MA Crossover":
        # Récupère les paramètres de la stratégie MA Crossover
        short_window = params.get('short_window', 50)
        long_window = params.get('long_window', 200)
        return calculate_ma_crossover(prices, short_window, long_window)
    
    # Retourne une série vide si la stratégie n'est pas reconnue
    return pd.Series(dtype=float)


if __name__ == '__main__':
    # --- Bloc de test pour le module (inchangé) ---
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