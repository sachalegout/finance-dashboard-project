# src/quant_b/config.py

# Liste d'actifs pour le Module B (Actions et Santé/Stable, avec des prix bruts comparables)
# GOOGL (Tech), AMZN (E-commerce/Cloud), JNJ (Santé/Stable)
TICKERS_B = ["GOOGL", "AMZN", "JNJ"]

# Couleurs pour le graphique des prix bruts
# Rouge (RED), Bleu (BLUE), Blanc/Gris (WHITE/LIGHTGRAY)
COLORS_B = {
    "GOOGL": "red",
    "AMZN": "blue",
    "JNJ": "lightgray" 
}