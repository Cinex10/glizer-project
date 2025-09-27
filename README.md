# 🎮 Glizer Bot Processor API v2.0

**Système automatisé de recharge UC PUBG avec rotation intelligente des credentials**

## 📋 Description

Glizer Bot Processor est une API FastAPI qui automatise le processus de recharge d'UC (Unknown Cash) pour PUBG Mobile via MidasBuy. Le système gère 10 bots simultanément avec une rotation automatique des credentials pour optimiser les performances et éviter les limitations.

### ✨ Fonctionnalités principales

- 🤖 **10 bots simultanés** : Traitement parallèle pour les bots 1-10
- 🔄 **Rotation automatique des credentials** : Gestion intelligente de 200+ comptes
- 🎯 **Support PUBG Mobile** : Intégration complète avec MidasBuy
- 📊 **Monitoring en temps réel** : Statistiques détaillées et suivi des transactions
- 🛡️ **Gestion d'erreurs robuste** : Retry automatique et classification des échecs
- 🗄️ **Base de données PostgreSQL** : Persistance et historique des transactions
- 📱 **API REST complète** : Interface pour intégration externe

## 🏗️ Architecture

```
glizer-project/
├── src/
│   ├── main.py                 # Point d'entrée FastAPI
│   ├── database/
│   │   ├── models.py          # Modèles SQLAlchemy
│   │   └── postgresql.py      # Configuration PostgreSQL
│   ├── services/
│   │   ├── transaction_processor.py  # Processeur principal
│   │   ├── credential_manager.py     # Gestion des credentials
│   │   └── bot_poller.py            # Polling des transactions
│   ├── pubg/
│   │   └── service.py         # Service d'automatisation PUBG
│   ├── config/
│   │   └── accounts.json      # 200+ credentials rotatifs
│   └── schemas.py             # Modèles Pydantic
├── requirements.txt           # Dépendances Python
├── init_database.py          # Script d'initialisation DB
└── create_table.sql          # Schéma de base de données
```

## 🚀 Installation et Configuration

### 1. Prérequis

- Python 3.8+
- PostgreSQL 12+
- Chrome/Chromium
- ChromeDriver

### 2. Installation

```bash
# Cloner le projet
git clone <repository-url>
cd glizer-project

# Créer l'environnement virtuel
python3 -m venv mon_env
source mon_env/bin/activate  # Linux/Mac
# ou
mon_env\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configuration PostgreSQL

```bash
# Créer la base de données
sudo -u postgres psql
CREATE DATABASE glizer_db;
CREATE USER glizer_user WITH PASSWORD 'glizer_pass';
GRANT ALL PRIVILEGES ON DATABASE glizer_db TO glizer_user;
\q
```

### 4. Configuration des variables d'environnement

```bash
# Copier le fichier d'exemple
cp src/env.example .env

# Éditer les variables
nano .env
```

**Configuration `.env` :**
```env
# Configuration PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=glizer_db
POSTGRES_USER=glizer_user
POSTGRES_PASSWORD=glizer_pass

# Configuration API
PORT=8000
LOG_LEVEL=INFO

# Configuration des workers
MAX_WORKERS=10
POLL_INTERVAL=30
```

### 5. Initialisation de la base de données

```bash
# Créer les tables
python3 init_database.py

# Ou avec des données d'exemple
python3 init_database.py --with-samples
```

## 🎯 Utilisation

### Démarrage de l'API

```bash
# Activer l'environnement virtuel
source mon_env/bin/activate

# Démarrer l'API
cd src
python3 main.py
```

L'API sera disponible sur `http://localhost:8000`

### Documentation interactive

- **Swagger UI** : `http://localhost:8000/docs`
- **ReDoc** : `http://localhost:8000/redoc`

## 📡 Endpoints API

### 🏥 Santé et Monitoring

```http
GET /health
GET /stats
GET /bot/{bot_num}/stats
```

### 📋 Gestion des Transactions

```http
GET /transactions?bot_num=9&status=pending&limit=50
GET /transaction/{transaction_id}
POST /transaction/{transaction_id}/process
POST /process/pending
```

### 🔐 Gestion des Credentials

```http
GET /credentials/status
POST /credentials/rotate
POST /credentials/reset?index=0
```

### 📧 Gestion des Emails

```http
GET /emails/status
POST /emails/release-all
```

### ⚙️ Maintenance

```http
GET /queue/status
POST /queue/clear-processing
GET /queue/processing/{transaction_id}
```

## 🔧 Ajout de Transactions

### Via l'API

```bash
# Ajouter une transaction
curl -X POST "http://localhost:8000/transaction" \
  -H "Content-Type: application/json" \
  -d '{
    "bot_num": 9,
    "player_id": "533938203",
    "code": "UCCODE123",
    "email": "player@example.com",
    "password": "playerpass"
  }'
```

### Via le script

```bash
# Ajouter une transaction
python3 add_transaction.py add 9 533938203 "UCCODE123" player@example.com playerpass

# Lister les transactions
python3 add_transaction.py list

# Voir les statistiques
python3 add_transaction.py stats
```

## 🎮 Fonctionnement du Bot PUBG

### Processus d'automatisation

1. **Connexion** : Le bot se connecte à MidasBuy avec les credentials rotatifs
2. **Authentification** : Login automatique avec email/password
3. **Sélection du joueur** : Changement vers le Player ID cible
4. **Rédemption** : Saisie et validation du code UC
5. **Vérification** : Confirmation du succès ou échec
6. **Rotation** : Passage au credential suivant

### Types d'erreurs gérées

- `wrong_player_id` : Player ID incorrect
- `wrong_code` : Code de rédemption invalide
- `wrong_item_type` : Type d'item incorrect
- `wrong_amount` : Montant incorrect
- `wrong_email_password` : Credentials invalides
- `other` : Autres erreurs

## 📊 Monitoring et Statistiques

### Dashboard en temps réel

```bash
# Statistiques globales
curl http://localhost:8000/stats

# Statistiques par bot
curl http://localhost:8000/bot/9/stats

# Statut des credentials
curl http://localhost:8000/credentials/status
```

### Logs

Les logs sont disponibles dans le dossier `logs/` avec rotation automatique.

## 🔄 Rotation des Credentials

Le système gère automatiquement 200+ comptes avec :

- **Rotation intelligente** : Passage automatique au credential suivant
- **Gestion des limites** : Évite les blocages par surutilisation
- **Monitoring** : Suivi de l'utilisation de chaque credential
- **Récupération** : Libération automatique des emails bloqués

## 🛠️ Maintenance

### Nettoyage des transactions

```bash
# Nettoyer les transactions en cours
curl -X POST http://localhost:8000/queue/clear-processing

# Libérer tous les emails
curl -X POST http://localhost:8000/emails/release-all
```

### Redémarrage propre

```bash
# Arrêt gracieux
pkill -f "python3 main.py"

# Redémarrage
cd src && python3 main.py
```

## 🐳 Déploiement Docker (Optionnel)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python3", "src/main.py"]
```

```bash
# Build et run
docker build -t glizer-api .
docker run -p 8000:8000 --env-file .env glizer-api
```

## 🔒 Sécurité

- **Credentials chiffrés** : Stockage sécurisé des mots de passe
- **Rotation automatique** : Réduction des risques de détection
- **Logs sécurisés** : Pas de credentials dans les logs
- **Validation stricte** : Contrôles sur tous les inputs

## 📈 Performance

- **10 workers simultanés** : Traitement parallèle optimisé
- **Base de données indexée** : Requêtes rapides
- **Gestion mémoire** : Optimisation des ressources
- **Retry intelligent** : Gestion des échecs temporaires

## 🆘 Dépannage

### Problèmes courants

1. **Erreur de connexion PostgreSQL**
   ```bash
   # Vérifier la configuration
   psql -h localhost -U glizer_user -d glizer_db
   ```

2. **ChromeDriver manquant**
   ```bash
   # Installer ChromeDriver
   sudo apt-get install chromium-chromedriver
   ```

3. **Credentials épuisés**
   ```bash
   # Vérifier le statut
   curl http://localhost:8000/credentials/status
   ```

### Logs de debug

```bash
# Activer les logs détaillés
export LOG_LEVEL=DEBUG
python3 src/main.py
```

## 📞 Support

Pour toute question ou problème :

1. Vérifier les logs dans `logs/`
2. Consulter l'API `/health` et `/stats`
3. Vérifier la configuration PostgreSQL
4. Tester avec des données d'exemple

## 📄 Licence

Projet privé - Tous droits réservés

---

**Glizer Bot Processor v2.0** - Automatisation PUBG UC avec rotation intelligente des credentials