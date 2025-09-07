# 🎮 PUBG Recharge Bot API

Bot automatisé pour les recharges PUBG Mobile avec API REST simple et efficace.

## 🚀 **Installation Rapide**

### **1. Prérequis**
- Python 3.8+
- Chrome/Chromium installé
- ChromeDriver dans le PATH

### **2. Installation**
```bash
# Cloner le projet
git clone <-repo>
cd glizer-project

# Installer les dépendances
pip install -r requirements.txt
```

### **3. Démarrage**
```bash
cd src
python main.py
```

L'API sera disponible sur : `http://localhost:8000`

## 📡 **API Endpoints**

### **Créer une Transaction**
```bash
curl -X POST "http://localhost:8000/transaction/create" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "votre@email.com",
    "password": "votre_mot_de_passe",
    "player_id": "123456789",
    "redeem_codes": ["CODE1"]
  }'
```

**Réponse :**
```json
{
  "transaction_id": "uuid-de-la-transaction",
  "status": "pending",
  "message": "Transaction created and queued for processing"
}
```

### **Vérifier le Statut d'une Transaction**
```bash
curl "http://localhost:8000/transaction/{transaction_id}"
```

**Réponse :**
```json
{
  "transaction_id": "uuid-de-la-transaction",
  "status": "success",
  "created_at": "2024-01-15T10:30:00",
  "started_at": "2024-01-15T10:30:05",
  "completed_at": "2024-01-15T10:32:15",
  "retry_count": 0,
  "max_retries": 3,
  "result": {
    "CODE1": true,
    "CODE2": true,
    "CODE3": false
  },
  "error_message": null
}
```

### **Lister les Transactions**
```bash
curl "http://localhost:8000/transactions?limit=50"
```

### **Statistiques du Système**
```bash
curl "http://localhost:8000/stats"
```

**Réponse :**
```json
{
  "total_transactions": 150,
  "success_rate": 75.5,
  "status_breakdown": {
    "pending": 5,      // En attente
    "processing": 2,   // En cours d'exécution
    "success": 110,    // Réussies
    "failed": 33       // Échouées après 3 tentatives
  },
  "thread_manager": {
    "running": true,
    "active_threads": 1,
    "max_workers": 1,
    "pending_transactions": 5,
    "processing_transactions": 2
  }
}
```

### **Réinitialiser la Base de Données**
```bash
curl -X POST "http://localhost:8000/reset-database"
```

### **Vérifier la Santé du Système**
```bash
curl "http://localhost:8000/health"
```

## 📊 **Statuts des Transactions**

| Statut | Description |
|--------|-------------|
| `pending` | En attente de traitement |
| `processing` | En cours d'exécution |
| `success` | Réussie (même partiellement) |
| `failed` | Échouée après 3 tentatives |

## 🔄 **Système de Retry**

- **Maximum 3 tentatives** par transaction
- **Retry automatique** en cas d'échec temporaire
- **Succès partiel** : Si 2 codes sur 3 réussissent, la transaction est marquée comme `success`

## 📁 **Structure du Projet**

```
glizer-project/
├── src/
│   ├── main.py              # API FastAPI principale
│   ├── models.py            # Modèles de base de données
│   ├── database.py          # Configuration SQLite
│   ├── thread_manager.py    # Gestionnaire de threads
│   ├── schemas.py           # Schémas Pydantic
│   ├── pubg_automation.py   # Wrapper pour le service
│   ├── pubg/
│   │   └── service.py       # Service Selenium
│   └── clean_database.py    # Script de nettoyage
├── data/                    # Base de données SQLite
├── screenshots/             # Captures d'écran de debug
├── user-data/               # User data Chrome par email
├── requirements.txt         # Dépendances Python
└── README.md               # Ce fichier
```



## 🔧 **Configuration**

### **Variables d'Environnement (optionnel)**
Créez un fichier `.env` dans le dossier `src/` :
```env
PORT=8000
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./data/transactions.db
```

### **Nettoyage de la Base de Données**
```bash
cd src
python clean_database.py stats          # Voir les statistiques
python clean_database.py clean-failed   # Supprimer les échecs
python clean_database.py clean-all      # Supprimer tout
```

## 📝 **Logs et Debug**

- **Logs** : Affichés dans le terminal
- **Captures d'écran** : Sauvegardées dans `screenshots/`
- **Base de données** : `data/transactions.db`

## ⚡ **Performance**

- **1 worker** traite les transactions en FIFO
- **User data partagé** pour le même email
- **Retry intelligent** avec backoff
- **Base de données optimisée** avec SQLite


