# 🔄 Glizer Credential Rotation System

Système de rotation automatique des credentials pour les recharges PUBG Mobile avec 20 comptes en rotation séquentielle.

## 🚀 **Nouveautés v3.0**

### ✅ **Système de Rotation Implémenté**
- **20 credentials** en rotation séquentielle
- **2 workers** qui utilisent les credentials de manière rotative
- **Queue intelligente** pour distribuer les transactions
- **Persistance de l'état** de rotation
- **Statistiques d'utilisation** par credential

### 🔧 **Architecture Modifiée**

```
glizer-project/
├── src/
│   ├── config/
│   │   ├── confidential.json         # 20 credentials en rotation
│   │   └── rotation_state.json       # État de rotation (auto-généré)
│   ├── services/
│   │   ├── credential_manager.py     # Gestionnaire de rotation
│   │   ├── bot_poller.py            # Polling PostgreSQL
│   │   └── transaction_processor.py  # Processeur avec rotation
│   ├── thread_manager.py            # Workers avec queue intelligente
│   ├── main.py                      # API adaptée
│   └── test_rotation.py             # Tests de rotation
```

## 📊 **Workflow de Rotation**

1. **Polling** → Surveille PostgreSQL toutes les 30s
2. **Queue** → Ajoute les transactions à une queue interne
3. **Workers** → 2 workers disponibles prennent les transactions
4. **Rotation** → Chaque worker utilise le prochain credential séquentiellement
5. **Traitement** → Automatisation PUBG avec le credential assigné
6. **Statut** → Mise à jour des statuts et statistiques

## 🔄 **Rotation des Credentials**

### **Cycle de Rotation**
- **Credential 1** → **Credential 2** → ... → **Credential 20** → **Credential 1**
- **Rotation automatique** après chaque transaction
- **Reset automatique** à la fin du cycle
- **Persistance** de la position actuelle

### **Gestion des Workers**
- **Worker 1** : Utilise credential N
- **Worker 2** : Utilise credential N+1
- **Pas d'assignation fixe** par bot_num
- **Distribution intelligente** selon disponibilité

## 📡 **API Endpoints Nouveaux**

### **Statut des Credentials**
```bash
# Vérifier l'état de rotation
curl "http://localhost:8000/credentials/status"

# Forcer la rotation
curl -X POST "http://localhost:8000/credentials/rotate"

# Reset de la rotation
curl -X POST "http://localhost:8000/credentials/reset?index=0"
```

### **Queue de Traitement**
```bash
# Statut de la queue
curl "http://localhost:8000/queue/status"

# Statistiques complètes avec rotation
curl "http://localhost:8000/stats"
```

## 📋 **Configuration des Credentials**

### **Fichier confidential.json**
```json
[
  {
    "id": 1,
    "email": "account1@example.com",
    "password": "Password123!"
  },
  {
    "id": 2,
    "email": "account2@example.com",
    "password": "Password123!"
  }
  // ... 18 autres credentials
]
```

### **État de Rotation (auto-généré)**
```json
{
  "current_index": 5,
  "usage_stats": {
    "1": {
      "email": "account1@example.com",
      "usage_count": 10,
      "last_used": "2024-01-15T10:30:00",
      "success_count": 8,
      "failed_count": 2
    }
  },
  "last_updated": "2024-01-15T10:30:00"
}
```

## 🧪 **Tests de Rotation**

### **Lancer les Tests**
```bash
cd src
python test_rotation.py
```

### **Tests Inclus**
- ✅ **CredentialManager** : Rotation et persistance
- ✅ **TransactionProcessor** : Intégration rotation
- ✅ **Rotation Cycle** : Cycle complet
- ✅ **State Persistence** : Sauvegarde/chargement état

## 📊 **Statistiques Avancées**

### **Statistiques par Credential**
- **Usage count** : Nombre d'utilisations
- **Success rate** : Taux de succès
- **Last used** : Dernière utilisation
- **Success/Failed counts** : Compteurs détaillés

### **Statistiques Globales**
- **Position actuelle** dans la rotation
- **Progression** (ex: "5/20")
- **Workers disponibles**
- **Taille de la queue**

## 🔒 **Sécurité et Gestion**

### **Verrouillage Thread-Safe**
- **Mutex** pour la rotation des credentials
- **Queue thread-safe** pour les transactions
- **Locks** pour les workers

### **Gestion d'Erreurs**
- **Retry automatique** avec rotation
- **Marquage des échecs** par credential
- **Récupération d'état** au redémarrage

## 🚀 **Démarrage**

### **1. Configuration**
```bash
# Vérifier les credentials
cat config/confidential.json

# Lancer les tests
python test_rotation.py
```

### **2. Démarrage de l'API**
```bash
python main.py
```

### **3. Vérification**
```bash
# Statut des credentials
curl "http://localhost:8000/credentials/status"

# Statistiques avec rotation
curl "http://localhost:8000/stats"
```

## 📈 **Avantages de la Rotation**

### ✅ **Performance**
- **Répartition de charge** sur 20 comptes
- **Évitement des limitations** de rate
- **Traitement parallèle** optimisé

### ✅ **Fiabilité**
- **Redondance** avec 20 credentials
- **Récupération automatique** en cas d'échec
- **Monitoring** détaillé par credential

### ✅ **Scalabilité**
- **Ajout facile** de nouveaux credentials
- **Ajustement** du nombre de workers
- **Monitoring** en temps réel

## 🔧 **Maintenance**

### **Ajouter des Credentials**
1. Éditer `config/confidential.json`
2. Redémarrer l'API
3. Vérifier avec `/credentials/status`

### **Reset de Rotation**
```bash
curl -X POST "http://localhost:8000/credentials/reset?index=0"
```

### **Monitoring**
- **Logs détaillés** de chaque rotation
- **API endpoints** pour surveillance
- **Tests automatiques** inclus

---

**Le système de rotation est maintenant opérationnel ! 🎉**

Les 2 workers tournent automatiquement sur les 20 credentials, avec une queue intelligente qui distribue les transactions aux workers disponibles, tout en maintenant la même fonctionnalité d'automatisation PUBG.

