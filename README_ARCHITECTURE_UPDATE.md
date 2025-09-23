# Mise à jour de l'architecture de la base de données PostgreSQL

## Vue d'ensemble

L'architecture de la base de données a été mise à jour pour correspondre exactement aux spécifications Salla pour l'intégration avec leur système.

## Changements apportés

### 1. Table `bots_transactions` - Structure simplifiée

**Avant :**
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

**Après :**
```sql
CREATE TABLE bots_transactions (
    id VARCHAR PRIMARY KEY,
    bot_num INTEGER NOT NULL CHECK (bot_num >= 1 AND bot_num <= 10),
    status VARCHAR DEFAULT 'pending',
    payload JSONB,
    bot_type VARCHAR NOT NULL CHECK (bot_type IN ('yalla_ludo', 'pubg'))
);
```

### 2. Structure du payload mise à jour

**Avant :**
```json
{
    "player_id": "533938203",
    "codes": ["TESTCODE1", "TESTCODE2"]
}
```

**Après :**
```json
{
    "player_id": "533938203",
    "code": "TESTCODE1",
    "email": "player@example.com",
    "password": "playerpassword"
}
```

### 3. Validation des données

- **bot_num** : Doit être un entier entre 1 et 10
- **bot_type** : Doit être soit "yalla_ludo" soit "pubg"
- **status** : "pending", "success", ou "failure"

### 4. Modèle SQLAlchemy mis à jour

Le modèle `BotTransaction` a été simplifié et aligné sur les spécifications :

```python
class BotTransaction(Base):
    __tablename__ = "bots_transactions"
    
    id = Column(String, primary_key=True)
    bot_num = Column(Integer, nullable=False)
    status = Column(String, default="pending")
    payload = Column(JSON)
    bot_type = Column(String, nullable=False)
    
    # Contraintes de validation
    __table_args__ = (
        CheckConstraint('bot_num >= 1 AND bot_num <= 10', name='check_bot_num_range'),
        CheckConstraint("bot_type IN ('yalla_ludo', 'pubg')", name='check_bot_type_valid'),
    )
```

## Fichiers modifiés

1. **`create_table.sql`** - Script de création de table mis à jour
2. **`src/database/models.py`** - Modèle SQLAlchemy simplifié
3. **`src/models.py`** - Fichier obsolète, redirige vers le nouveau modèle
4. **`migrate_database.sql`** - Script de migration pour les bases existantes

## Nouveaux fichiers

1. **`test_new_architecture.py`** - Script de test de la nouvelle architecture
2. **`example_salla_integration.py`** - Exemple d'intégration avec Salla
3. **`README_ARCHITECTURE_UPDATE.md`** - Cette documentation

## Migration des données existantes

Pour migrer une base de données existante :

1. **Sauvegardez vos données** :
   ```sql
   CREATE TABLE bots_transactions_backup AS SELECT * FROM bots_transactions;
   ```

2. **Exécutez le script de migration** :
   ```bash
   psql -h your_host -U your_user -d your_database -f migrate_database.sql
   ```

3. **Vérifiez la structure** :
   ```sql
   \d bots_transactions
   ```

## Utilisation avec les données Salla

### Création d'une transaction

```python
from src.database.models import BotTransaction

# Données venant de Salla
salla_data = {
    "bot_num": 9,
    "bot_type": "pubg",
    "payload": {
        "player_id": "533938203",
        "code": "PUBGCODE123",
        "email": "player@example.com",
        "password": "playerpassword"
    }
}

# Créer la transaction
transaction = BotTransaction(
    id="unique-id",
    bot_num=salla_data['bot_num'],
    status="pending",
    payload=salla_data['payload'],
    bot_type=salla_data['bot_type']
)
```

### Traitement et mise à jour du statut

```python
# Traiter la transaction (votre logique d'automatisation)
success = process_automation(transaction)

# Mettre à jour le statut
transaction.status = "success" if success else "failure"
session.commit()
```

## Tests

Exécutez les tests pour vérifier que tout fonctionne :

```bash
python test_new_architecture.py
```

## Intégration Salla

L'architecture est maintenant prête pour recevoir les vraies requêtes de Salla. Le système peut :

1. **Recevoir** les requêtes avec les données spécifiées
2. **Valider** les données selon les contraintes
3. **Traiter** les opérations d'automatisation
4. **Mettre à jour** le statut (success/failure)

## Notes importantes

- Les colonnes de suivi (created_at, updated_at, etc.) ont été supprimées pour simplifier
- Le payload contient maintenant email et password en plus de player_id et code
- Les contraintes de validation sont appliquées au niveau base de données
- L'ancien modèle `Transaction` est obsolète, utilisez `BotTransaction`

## Support

Cette architecture respecte exactement les spécifications Salla et est prête pour la production.

