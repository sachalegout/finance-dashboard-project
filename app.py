# app.py (CODE CORRIGÉ)
import streamlit as st
from src.quant_a.dashboard import run_quant_a_dashboard

# Import adapté : on importe depuis src.quant_b.dashboard_b.py
try:
    # 🟢 CORRECTION : Utiliser le nom du fichier 'dashboard_b'
    from src.quant_b.dashboard_b import run_quant_b_dashboard
    B_MODULE_EXISTS = True
except ImportError:
    # Si cette erreur se produit encore, cela signifie qu'une erreur interne
    # dans dashboard_b.py (syntaxe ou import relatif) bloque l'importation.
    B_MODULE_EXISTS = False

# Configuration générale de la page
st.set_page_config(
    page_title="Dashboard Quant pour Asset Management",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("💼 Plateforme Quant de Recherche Financièr")
st.caption("Conçu pour le support des Portfolio Managers à Paris.")

# Sidebar pour la navigation (intégration des deux modules)
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Choisissez votre module :",
    ["Module Quant A (NVIDIA)", "Module Quant B (Portefeuille)"]
)

if page == "Module Quant A (NVIDIA)":
    run_quant_a_dashboard()
    
elif page == "Module Quant B (Portefeuille)":
    if B_MODULE_EXISTS:
        # 🟢 APPEL RÉUSSI : Ceci devrait maintenant lancer le Module B
        run_quant_b_dashboard() 
    else:
        # Message de secours (ne devrait plus s'afficher)
        st.header("Module Portefeuille Multi-Actifs (Quant B)")
        st.error("Ce module est en cours de préparation par votre partenaire (Quant B). L'importation du module a échoué.")