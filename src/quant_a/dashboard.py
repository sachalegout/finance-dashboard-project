# src/quant_a/dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px  # <-- NOUVEL IMPORT PLOTLY
import numpy as np
# Import des fonctions de récupération de données
from src.quant_a.data_handler import get_historical_data, get_realtime_price, TICKER
# Import des fonctions de backtesting et métriques
from src.quant_a.strategy_engine import run_backtest, calculate_metrics
    
# Utilisation du cache Streamlit pour gérer le rafraîchissement des données (Core Feature 5)
@st.cache_data(ttl=300) # Mise à jour toutes les 300 secondes (5 minutes)
def load_data(period):
    """Fonction sécurisée pour charger les données historiques."""
    return get_historical_data(period=period)

def run_quant_a_dashboard():
    """Contient la logique de l'interface et de l'affichage pour le module Quant A."""
    
    st.title("💡 NVIDIA : Analyse de l'Actif Unique (Module Quant A)")
    st.subheader("Simulations de Stratégie et Métriques de Performance")
    
    st.markdown("---")

    # --- Section 1 : Prix Actuel et Rafraîchissement (Core Feature 3 & 5) ---
    current_price = get_realtime_price()
    
    st.markdown("#### 🟢 Données Actuelles")
    col1, col2, col3 = st.columns([1, 1, 3])
    
    with col1:
        # Affichage du Prix Actuel
        st.metric(label=f"Prix Actuel {TICKER}", value=f"${current_price}")
        
    with col2:
        # Affichage de l'heure de la dernière mise à jour
        st.caption(f"Dernière mise à jour: {pd.Timestamp.now().strftime('%H:%M:%S')}")
        
    with col3:
        st.caption("Les données se rafraîchissent automatiquement toutes les 5 minutes.")
    
    st.markdown("---")

    # --- Section 2 : Contrôles Interactifs (Période et Stratégie) ---
    
    st.markdown("#### ⚙️ Paramètres de Backtesting")
    
    col_select_period, col_select_strategy = st.columns(2)
    
    with col_select_period:
        period_options = {
            "1 Mois": "1mo", 
            "3 Mois": "3mo", 
            "6 Mois": "6mo", 
            "1 An": "1y",
            "3 Ans": "3y" # Ajout de 3 ans pour une meilleure analyse du Max Drawdown
        }
        selected_period_label = st.selectbox(
            "Sélecteur de Période Historique :",
            options=list(period_options.keys()),
            index=3 
        )
        selected_period = period_options[selected_period_label]
        
    with col_select_strategy:
        selected_strategy = st.selectbox(
            "Sélecteur de Stratégie (Min. 2 requises) :",
            options=["Buy-and-Hold", "MA Crossover"]
        )
    
    # --- Contrôles de Paramètres Interactifs pour la Stratégie (via expander) ---
    strategy_params = {}
    if selected_strategy == "MA Crossover":
        with st.expander("Configurer la Stratégie MA Crossover"):
            col_short, col_long = st.columns(2)
            
            with col_short:
                short_window = st.slider("Fenêtre Courte (jours)", min_value=10, max_value=100, value=50, step=5)
                strategy_params['short_window'] = short_window
                
            with col_long:
                long_window = st.slider("Fenêtre Longue (jours)", min_value=50, max_value=300, value=200, step=10)
                strategy_params['long_window'] = long_window

    # Récupération des données historiques via la fonction cachée
    historical_data = load_data(selected_period)
    
    if not historical_data.empty:
        
        # 1. Exécution du Backtest 
        strategy_results = run_backtest(historical_data, selected_strategy, **strategy_params)
        
        # 2. Préparation des données pour le graphique (Normalisation base 100)
        prices = historical_data['Price']
        first_price = prices.iloc[0]
        # Normalise le prix de l'actif pour qu'il commence à 100.0
        normalized_price = (prices / first_price) * 100.0
        
        # Crée le DataFrame final pour le graphique
        chart_data = pd.DataFrame({
            'Prix Normalisé (Actif)': normalized_price.values.ravel(), 
            f'Valeur Cumulée ({selected_strategy})': strategy_results.values.ravel() 
        }, index=historical_data.index)
        
        # --- Section 3 : Graphique Interactif (Core Feature 4) ---
        st.markdown("#### 📊 Performance Cumulée (Base 100)")
        
        # Préparation du DataFrame pour Plotly
        chart_data_reset = chart_data.reset_index()
        chart_data_reset = chart_data_reset.rename(columns={'index': 'Date'})

        # Utilisation de Plotly pour l'interactivité
        fig = px.line(
            chart_data_reset, 
            x='Date', 
            y=chart_data_reset.columns[1:],
            title=f"Comparaison de la performance de la stratégie {selected_strategy} (vs. Prix Actif)",
            labels={'value': 'Valeur Normalisée (Base 100)'}
        )
        fig.update_layout(legend_title_text='Séries', hovermode="x unified")
        
        # Affichage du graphique Plotly
        st.plotly_chart(fig, use_container_width=True)

        # --- Section 4 : Métriques de Performance (Division of Work) ---
        st.markdown("#### 📋 Métriques de Performance Clés")
        
        metrics = calculate_metrics(strategy_results)
        
        # Extraction des valeurs scalaires
        final_value = strategy_results.iloc[-1].item() 
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        # Affichage des métriques dans des colonnes pour un look professionnel
        with col_m1:
            st.metric(
                label="Rendement Total Stratégie", 
                value=f"{final_value - 100:.2f} %",
                delta=f"{(final_value - 100) / 100:.2%}" if final_value > 100 else f"{(final_value - 100) / 100:.2%}", # Delta en pourcentage
                delta_color="normal"
            )
        
        with col_m2:
            st.metric(
                label="Sharpe Ratio (Annuel)", 
                value=metrics['Sharpe Ratio (Annuel)']
            )
            
        with col_m3:
            st.metric(
                label="Max Drawdown", 
                value=metrics['Max Drawdown']
            )

        with col_m4:
             # Ajout d'une métrique simple pour compléter
            st.metric(
                label="Jours d'Analyse", 
                value=len(historical_data)
            )
            
    else:
        # Gestion d'erreur (Robustness)
        st.error("⚠️ Impossible de charger les données historiques ou données vides. Veuillez vérifier le ticker ou la connexion API.")