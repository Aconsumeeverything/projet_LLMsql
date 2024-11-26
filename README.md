# Projet LLM SQL

  Ce projet est un **générateur et exécuteur de requêtes SQL à partir de langage naturel**, développé avec l'API SambaNova et Gradio. Il permet aux utilisateurs d’interagir avec une base de données PostgreSQL en posant des questions en langage naturel. L'application traduit ces questions en requêtes SQL, les exécute sur la base de données et affiche les résultats.

## Fonctionnalités
- Conversion du langage naturel en requêtes SQL.
- Intégration avec une base de données PostgreSQL.
- Interface interactive construite avec Gradio.
- Déployé via Docker pour une utilisation simplifiée.
- Inclut des exemples pour démarrer rapidement.

---

## Prérequis
1. Une clé API fonctionnelle obtenue depuis :
   - [SambaNova](https://www.sambanova.ai/) (ou un autre fournisseur d'API comme OpenAI). (une fois vous avez votre clé d Api penser a la mettre sur "api_key" sur le  fichier main.py)
2. Outils nécessaires :
   - [Python 3.9](https://www.python.org/)
   - [Docker](https://www.docker.com/)
   - [Docker Compose](https://docs.docker.com/compose/)

---

## Installation

1. **Cloner le dépôt Git** :
   ```bash
   # sur votre terminale exécuter ses commandes
   git clone https://github.com/username/projet_LLMsql.git
   cd projet_LLMsql
   docker-compose up -d
   ```
## Visulalisation 
  Une fois l'installation est terminée lancer le script python et sur un navigateur visiter le local URL:  (http://127.0.0.1:7860)



