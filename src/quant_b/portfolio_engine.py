# src/quant_b/portfolio_engine.py
import pandas as pd
import numpy as np

def calculate_portfolio_metrics(prices: pd.DataFrame, weights: np.ndarray, risk_free_rate=0.04) -> dict:
    """
    Calcule les métriques de performance et de risque pour le portefeuille donné.

    :param prices: pd.DataFrame des prix des actifs (colonnes = tickers).
    :param weights: np.ndarray des pondérations des actifs (doit sommer à 1).
    :param risk_free_rate: Taux sans risque annuel.
    :return: dict des métriques du portefeuille.
    """
    if prices.empty:
        return {"Annualized Return": "N/A", "Annualized Volatility": "N/A", "Sharpe Ratio": "N/A"}

    # 1. Calcul des rendements quotidiens
    daily_returns = prices.pct_change().dropna()

    # 2. Rendement quotidien du portefeuille
    portfolio_daily_returns = daily_returns.dot(weights)

    # 3. Métriques annualisées
    annualization_factor = 252  # Jours de trading par an
    annual_return = portfolio_daily_returns.mean() * annualization_factor
    annual_volatility = portfolio_daily_returns.std() * np.sqrt(annualization_factor)
    
    # 4. Sharpe Ratio
    if annual_volatility == 0:
         sharpe_ratio = 0.0
    else:
         sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility

    # 5. Max Drawdown (Calculé sur la série de la valeur cumulée)
    cumulative_value = (1 + portfolio_daily_returns).cumprod()
    rolling_max = cumulative_value.cummax()
    drawdown = (cumulative_value / rolling_max) - 1
    max_drawdown = drawdown.min().item()

    # 6. Matrice de Corrélation
    correlation_matrix = daily_returns.corr()
    
    return {
        "Annualized Return": f"{annual_return * 100:.2f} %",
        "Annualized Volatility": f"{annual_volatility * 100:.2f} %",
        "Sharpe Ratio": f"{sharpe_ratio:.2f}",
        "Max Drawdown": f"{max_drawdown * 100:.2f} %",
        "Correlation Matrix": correlation_matrix # Retourne la DataFrame pour affichage
    }

def calculate_portfolio_value(prices: pd.DataFrame, weights: np.ndarray) -> pd.Series:
    """
    Calcule la valeur cumulée (Base 100) du portefeuille.
    """
    if prices.empty:
        return pd.Series(dtype=float)

    daily_returns = prices.pct_change().dropna()
    portfolio_daily_returns = daily_returns.dot(weights)
    
    # Valeur cumulée (Base 100)
    cumulative_value = (1 + portfolio_daily_returns).cumprod()
    cumulative_value = cumulative_value / cumulative_value.iloc[0] * 100.0
    
    return cumulative_value