# src/quant_b/dashboard_b.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from .config import TICKERS_B, COLORS_B
from .data_handler_b import get_historical_data_multi, get_realtime_prices_multi
from .portfolio_engine import calculate_portfolio_metrics, calculate_portfolio_value

@st.cache_data(ttl=300)
def load_data_b(period):
    """Fonction sécurisée pour charger les données historiques multi-actifs."""
    return get_historical_data_multi(period=period)

def run_quant_b_dashboard():
    """Contient la logique de l'interface pour le module Portefeuille Multi-Actifs."""
    
    st.header("🌐 Analyse de Portefeuille Multi-Actifs (Module Quant B)")
    st.caption(f"Actifs du portefeuille : {', '.join(TICKERS_B)}")

    # --- 1. Affichage des Prix Actuels ---
    realtime_prices = get_realtime_prices_multi()
    st.markdown("#### 🟢 Prix Actuels")
    cols_prices = st.columns(len(TICKERS_B))
    
    for i, ticker in enumerate(TICKERS_B):
        with cols_prices[i]:
            st.metric(label=f"Prix {ticker}", value=f"${realtime_prices.get(ticker, 'N/A')}")
    st.markdown("---")

    # --- 2. Contrôles Interactifs ---
    st.markdown("#### ⚙️ Paramètres du Portefeuille")
    
    col_period, col_strategy = st.columns(2)

    with col_period:
        period_options = {"1 An": "1y", "3 Ans": "3y", "5 Ans": "5y"}
        selected_period_label = st.selectbox("Période d'Analyse :", options=list(period_options.keys()), index=0)
        selected_period = period_options[selected_period_label]

    with col_strategy:
        selected_strategy = st.selectbox(
            "Sélectionnez la Stratégie de Pondération :", 
            options=["Equal Weight (Poids Égaux)", "Custom Weights (Poids Personnalisés)"]
        )
    
    with st.expander("Paramètres Avancés"):
        risk_free_rate = st.number_input(
            "Taux sans risque annuel (en %) :",
            min_value=0.0,
            max_value=10.0,
            value=4.0, 
            step=0.1,
            format="%.2f"
        ) / 100.0 # Convertir en décimal
    
    prices_df = load_data_b(selected_period)

    if prices_df.empty:
        st.error("⚠️ Impossible de charger les données pour le portefeuille. Vérifiez la connexion ou les tickers.")
        return

    # --- 3. Définition des Pondérations ---
    weights = []
    
    if selected_strategy == "Equal Weight (Poids Égaux)":
        weight_val = 1.0 / len(TICKERS_B)
        weights = np.array([weight_val] * len(TICKERS_B))
        st.info(f"Le portefeuille utilise des poids égaux de {weight_val * 100:.2f} % par actif.")

    elif selected_strategy == "Custom Weights (Poids Personnalisés)":
        st.markdown("##### ⚖️ Définition des Pondérations (Custom Weights)")
        
        cols_weights = st.columns(len(TICKERS_B))
        total_weights = 0
        weights_raw = []
        
        for i, ticker in enumerate(TICKERS_B):
            with cols_weights[i]:
                weight = st.slider(f"Poids {ticker} (%)", min_value=0, max_value=100, value=int(100/len(TICKERS_B)), key=f"weight_{ticker}")
                weights_raw.append(weight)
                total_weights += weight

        if total_weights != 100 and total_weights > 0:
            st.warning(f"La somme des poids est de {total_weights} %. Ils seront normalisés.")
            weights = np.array(weights_raw) / total_weights
        elif total_weights == 0:
            st.error("La somme des poids ne peut pas être zéro. Veuillez attribuer des poids.")
            return
        else:
            weights = np.array(weights_raw) / 100.0 # Normalise simplement à 1.0


    # --- 4. Graphique 1 : Évolution des Prix Bruts (NOUVEAU) ---
    st.markdown("#### 📉 Évolution des Prix Quotidiens (Valeurs Brutes)")
    
    # Préparation des données pour le graphique des prix bruts
    # Utilisation du DataFrame 'prices_df' tel quel (prix bruts)
    prices_raw_chart_data = prices_df.reset_index().melt(
        id_vars='Date', 
        var_name='Actif', 
        value_name='Prix Brut ($)'
    )
    
    # Création du Plotly Chart (Utilisation des couleurs demandées)
    fig_raw = px.line(
        prices_raw_chart_data,
        x='Date',
        y='Prix Brut ($)',
        color='Actif',
        color_discrete_map=COLORS_B, # Applique les couleurs configurées
        title="Prix Bruts des Actifs (sans normalisation)"
    )
    fig_raw.update_layout(hovermode="x unified")
    st.plotly_chart(fig_raw, use_container_width=True)

    st.markdown("---")

    # --- 5. Matrice de Corrélation ---
    st.markdown("#### 🔗 Matrice de Corrélation")
    metrics = calculate_portfolio_metrics(prices_df, weights, risk_free_rate=risk_free_rate)
    
    st.dataframe(metrics["Correlation Matrix"].style.background_gradient(cmap='coolwarm', axis=None).format("{:.2f}"))
    
    # --- 6. Affichage des Métriques de Portefeuille ---
    st.markdown("#### 📋 Métriques de Performance du Portefeuille")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Rendement Annuel", metrics["Annualized Return"])
    with col2:
        st.metric("Volatilité Annuelle", metrics["Annualized Volatility"])
    with col3:
        st.metric("Sharpe Ratio", metrics["Sharpe Ratio"])
    with col4:
        st.metric("Max Drawdown", metrics["Max Drawdown"])

    st.markdown("---")
    
    # --- 7. Graphique 2 : Valeur Cumulée Normalisée (CORRECTION) ---
    st.markdown("#### 📈 Comparaison de Performance (Valeur Cumulée Base 100)")
    
    # Calcul de la valeur cumulée du portefeuille
    portfolio_value = calculate_portfolio_value(prices_df, weights)
    
    # Normalisation des actifs individuels pour la comparaison
    normalized_assets = (prices_df / prices_df.iloc[0]) * 100.0
    
    # Création du DataFrame final pour le graphique (CONTIENT TOUS LES ACTIFS + PORTEFEUILLE)
    chart_data = normalized_assets.copy()
    chart_data['Portefeuille'] = portfolio_value

    fig = px.line(
        chart_data, 
        y=chart_data.columns, # Affiche TOUTES les colonnes
        title=f"Portefeuille ({selected_strategy}) vs. Actifs Individuels ({selected_period_label})",
        labels={'value': 'Valeur Normalisée (Base 100)', 'variable': 'Série'},
        x=chart_data.index
    )
    fig.update_traces(
        line=dict(width=3, dash='solid'), 
        selector=dict(name='Portefeuille')
    )
    fig.update_layout(legend_title_text='Séries', hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)