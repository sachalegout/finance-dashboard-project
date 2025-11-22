# finance-dashboard-project

## 💼 Plateforme Quant de Recherche Financière

Ce projet vise à créer une plateforme en ligne interactive pour l'analyse financière, intégrant Python, Streamlit, Git, et un déploiement Linux (VM).

### 🚀 Module A : Analyse Univariée (Quant A)

* **Actif Suivi :** NVIDIA Corporation (NVDA)
* **Fonctionnalités :**
    * Affichage du prix en temps réel (via yfinance).
    * Backtesting de deux stratégies : Buy-and-Hold et MA Crossover.
    * Affichage des métriques clés : Sharpe Ratio et Max-Drawdown.
    * Dashboard interactif Streamlit avec rafraîchissement toutes les 5 minutes.
    * [À ajouter par vous : Détails sur la fonctionnalité Bonus ML si vous l'implémentez].

### 🛠️ Configuration du Projet

1.  **Cloner le dépôt :** `git clone [votre_lien_repo]`
2.  **Créer l'environnement virtuel :** `python3 -m venv venv`
3.  **Activer l'environnement :** `source venv/bin/activate` (Linux) ou `.\venv\Scripts\Activate.ps1` (PowerShell)
4.  **Installer les dépendances :** `pip install -r requirements.txt`

### 💡 Déploiement et Rapports Quotidiens (Linux / Cron)

Le rapport quotidien est généré automatiquement par un job Cron.

1.  **Rapport (daily_report.py) :** Le script génère un fichier `data/daily_report_NVDA.txt` à 20h00.
2.  **Configuration Cron :** Pour mettre en place la tâche, utilisez la commande `crontab -e` sur votre VM Linux et ajoutez la ligne suivante (adaptez le chemin) :
    ```bash
    0 20 * * * /usr/bin/python3 /chemin/vers/votre/daily_report.py >> /chemin/vers/votre/cron.log 2>&1
    ```
3.  **Lancement du Dashboard (24/7) :** Pour garantir que l'application est toujours en cours d'exécution (Core Feature 7), utilisez `nohup` ou un service `systemd`. Exemple :
    ```bash
    nohup streamlit run app.py --server.port 8501 &
    ```
    *(Note : L'utilisation de systemd est la méthode professionnelle recommandée, à explorer si possible).*

---

## 4. Workflow GitHub

1.  **Effectuez les modifications** des étapes 1, 2 et 3 (sauf le `README`) dans votre branche actuelle (`feature/quant-a-nvidia`).
2.  **Committez les changements** : Utilisez des messages clairs (ex: `feat(dashboard): Implemented Plotly for interactive charts and improved UI` ou `fix(strategy): Added function docstrings for code quality`).
3.  **Push :** `git push origin feature/quant-a-nvidia`
4.  **Ouvrez un Pull Request (PR)** sur GitHub pour fusionner `feature/quant-a-nvidia` vers `main`. [cite_start]C'est une étape obligatoire[cite: 51].
5.  Une fois mergé, vous pourrez créer la branche pour le Module B (`feature/quant-b-portfolio`).

Voulez-vous que je vous aide à rédiger les premières structures pour le **Module Quant B** (fonctions de corrélation, pondérations) avant de passer à l'étape 4 ?