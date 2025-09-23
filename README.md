# 🤖 Glizer Bot Processor API v2.0

Système d'automatisation pour les recharges PUBG Mobile spécialement conçu pour traiter les bots 9 et 10 via une base de données PostgreSQL externe.

## 🚀 **Installation Rapide**

### **1. Prérequis**
- Python 3.8+
- Chrome/Chromium installé
- ChromeDriver dans PATH
- Base de données PostgreSQL accessible

### **2. Installation**
```bash
# Cloner le projet
git clone <repo>
cd glizer-project

# Installer les dépendances
pip install -r requirements.txt
```

### **3. Configuration**
```bash
# Copier le fichier d'environnement
cp src/env.example src/.env

# Éditer les variables PostgreSQL
nano src/.env
```

### **4. Configuration des Credentials**
```bash
# Éditer le fichier de credentials
nano src/config/credentials.json
```

### **5. Démarrage**
```bash
cd src
python main.py
```

L'API sera disponible sur : `http://localhost:8000`

## 📡 **API Endpoints**

### **Vérification de Santé**
```bash
curl "http://localhost:8000/health"
```

### **Statistiques des Bots**
```bash
curl "http://localhost:8000/stats"
```

### **Statistiques d'un Bot Spécifique**
```bash
curl "http://localhost:8000/bot/9/stats"
curl "http://localhost:8000/bot/10/stats"
```

### **Lister les Transactions**
```bash
# Toutes les transactions
curl "http://localhost:8000/transactions"

# Transactions d'un bot spécifique
curl "http://localhost:8000/transactions?bot_num=9"

# Transactions par statut
curl "http://localhost:8000/transactions?status=pending"
```

### **Statut d'une Transaction**
```bash
curl "http://localhost:8000/transaction/{transaction_id}"
```

### **Traiter une Transaction Manuellement**
```bash
curl -X POST "http://localhost:8000/transaction/{transaction_id}/process"
```

### **Traiter Toutes les Transactions en Attente**
```bash
curl -X POST "http://localhost:8000/process/pending"
```

### **Vérifier les Credentials**
```bash
curl "http://localhost:8000/credentials/status"
```

## 🔧 **Configuration**

### **Variables d'Environnement**
```env
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=glizer_db
POSTGRES_USER=glizer_user
POSTGRES_PASSWORD=glizer_pass

# API
PORT=8000
LOG_LEVEL=INFO
```

### **Credentials des Bots**
```json
{
  "bots": {
    "9": {
      "email": "bot9@example.com",
      "password": "password123"
    },
    "10": {
      "email": "bot10@example.com", 
      "password": "password456"
    }
  }
}
```

## 📊 **Structure de la Base de Données**

### **Table bots_transactions**
```sql
CREATE TABLE bots_transactions (
    id VARCHAR PRIMARY KEY,
    bot_num INTEGER NOT NULL,
    status VARCHAR DEFAULT 'pending',
    payload JSONB,
    bot_type VARCHAR DEFAULT 'pubg',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3
);
```

### **Format du Payload**
```json
{
  "player_id": "533938203",
  "codes": ["CODE1", "CODE2", "CODE3"]
}
```

## 🔄 **Workflow**

1. **Polling** : Le système vérifie la base PostgreSQL toutes les 30 secondes
2. **Filtrage** : Seules les transactions avec `bot_num IN (9, 10)` et `bot_type = "pubg"` sont traitées
3. **Traitement** : Chaque bot a son worker dédié pour le traitement en parallèle
4. **Authentification** : Utilise les credentials spécifiques à chaque bot
5. **Mise à jour** : Met à jour le statut : `pending → processing → success/failed`

## 📁 **Architecture**

```
glizer-project/
├── src/
│   ├── config/
│   │   └── credentials.json      # Credentials des bots
│   ├── database/
│   │   ├── postgresql.py         # Connexion PostgreSQL
│   │   └── models.py             # Modèles adaptés
│   ├── services/
│   │   ├── bot_poller.py         # Service de polling
│   │   └── transaction_processor.py # Traitement des transactions
│   ├── pubg/
│   │   └── service.py            # Selenium (inchangé)
│   ├── main.py                   # Point d'entrée FastAPI
│   ├── thread_manager.py         # Gestionnaire de threads
│   ├── schemas.py                # Schémas Pydantic
│   └── pubg_automation.py        # Wrapper Selenium
├── requirements.txt              # Dépendances Python
└── README.md                    # Ce fichier
```

## ⚡ **Fonctionnalités**

- ✅ **Traitement en Parallèle** : Workers dédiés pour bots 9 et 10
- ✅ **Polling Intelligent** : Surveillance continue de PostgreSQL
- ✅ **Retry Automatique** : 3 tentatives maximum par transaction
- ✅ **Credentials Séparés** : Configuration par bot
- ✅ **Logging Détaillé** : Suivi complet des opérations
- ✅ **API REST** : Interface complète pour monitoring
- ✅ **Gestion d'Erreurs** : Robustesse et récupération automatique

## 📝 **Logs et Debug**

- **Logs** : Affichés dans le terminal avec timestamps
- **Screenshots** : Sauvegardées dans `screenshots/`
- **Base de Données** : Toutes les opérations trackées dans PostgreSQL

## 🔒 **Sécurité**

- Credentials stockés dans un fichier JSON séparé
- Connexions PostgreSQL sécurisées
- Gestion des erreurs sans exposition de données sensibles
- Logs sanitaires (pas de mots de passe exposés)

## 🚨 **Statuts des Transactions**

| Statut | Description |
|--------|-------------|
| `pending` | En attente de traitement |
| `processing` | En cours d'exécution |
| `success` | Réussie (complète ou partielle) |
| `failed` | Échouée après 3 tentatives |

## 🔄 **Système de Retry**

- **Maximum 3 tentatives** par transaction
- **Retry automatique** en cas d'échec temporaire
- **Succès partiel** : Si au moins 1 code sur plusieurs réussit, la transaction est marquée comme `success`

## 📈 **Monitoring**

Utilisez les endpoints API pour surveiller :
- État de santé du système
- Statistiques par bot
- Transactions en cours
- Taux de succès
- Workers actifs