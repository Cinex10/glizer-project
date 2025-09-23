# 📦 Mise à jour du Format de Payload

## 🎯 **Changements Apportés**

### **Ancien Format (Supprimé)**
```json
{
  "player_id": "533938203",
  "codes": ["CODE1", "CODE2", "CODE3"]
}
```

### **Nouveau Format (Salla)**
```json
{
  "player_id": "533938203",
  "code": "SINGLE_CODE",
  "email": "player@example.com",
  "password": "playerpassword"
}
```

## 🔧 **Logique d'Utilisation**

### **Ce qui est utilisé par le code :**
- ✅ **`player_id`** : ID du joueur PUBG
- ✅ **`code`** : Code de rédemption unique

### **Ce qui est stocké mais NON utilisé :**
- ❌ **`email`** : Stocké dans la base mais ignoré
- ❌ **`password`** : Stocké dans la base mais ignoré

### **Ce qui est utilisé pour l'automatisation :**
- ✅ **Credentials rotatifs** : 20 comptes en rotation depuis `config/confidential.json`
- ✅ **Rotation automatique** : Chaque transaction utilise le prochain credential

## 📊 **Exemple de Transaction**

```sql
INSERT INTO bots_transactions (id, bot_num, status, payload, bot_type) VALUES
('txn-12345', 9, 'pending', 
 '{"player_id": "533938203", "code": "PUBGCODE123", "email": "player@example.com", "password": "playerpass"}', 
 'pubg');
```

**Traitement :**
1. **Extraction** : `player_id = "533938203"`, `code = "PUBGCODE123"`
2. **Credential rotatif** : Utilise le prochain credential de la rotation (ex: `Abdull82ah@hotmail.com`)
3. **Automatisation** : `process_pubg_transaction(email="Abdull82ah@hotmail.com", password="ZXCVzxcv@1010", player_id="533938203", redeem_codes=["PUBGCODE123"])`

## 🔄 **Workflow Complet**

```
Base de Données (PostgreSQL)
        ↓
Payload: {"player_id": "123", "code": "ABC", "email": "x", "password": "y"}
        ↓
Code utilise: player_id="123", code="ABC"
        ↓
Credential rotatif: email="Abdull82ah@hotmail.com", password="ZXCVzxcv@1010"
        ↓
Selenium: Login avec credential rotatif + Redeem code ABC pour player 123
```

## ✅ **Avantages**

1. **Compatibilité Salla** : Format conforme aux spécifications
2. **Sécurité** : Utilise vos credentials rotatifs (pas ceux du client)
3. **Performance** : Rotation sur 20 comptes pour éviter les limitations
4. **Flexibilité** : Stockage des données client + utilisation de vos credentials

## 🚨 **Points Importants**

- **Email/Password du payload** : Stockés mais **JAMAIS utilisés**
- **Credentials rotatifs** : Toujours utilisés pour l'automatisation
- **Format unique** : Un seul code par transaction (pas de tableau)
- **Compatibilité** : Méthode `get_redeem_codes()` convertit le code unique en tableau

## 📝 **Migration**

Si vous avez des données avec l'ancien format :
```sql
-- Convertir codes multiples en code unique (prendre le premier)
UPDATE bots_transactions 
SET payload = jsonb_set(
    payload - 'codes', 
    '{code}', 
    to_jsonb((payload->'codes'->0)::text)
)
WHERE payload ? 'codes';
```


