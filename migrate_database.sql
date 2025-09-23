-- Script de migration pour adapter la table bots_transactions
-- aux nouvelles spécifications Salla

-- 1. Sauvegarder les données existantes si nécessaire
-- CREATE TABLE bots_transactions_backup AS SELECT * FROM bots_transactions;

-- 2. Supprimer les colonnes qui ne sont plus nécessaires
ALTER TABLE bots_transactions DROP COLUMN IF EXISTS created_at;
ALTER TABLE bots_transactions DROP COLUMN IF EXISTS updated_at;
ALTER TABLE bots_transactions DROP COLUMN IF EXISTS started_at;
ALTER TABLE bots_transactions DROP COLUMN IF EXISTS completed_at;
ALTER TABLE bots_transactions DROP COLUMN IF EXISTS error_message;
ALTER TABLE bots_transactions DROP COLUMN IF EXISTS retry_count;
ALTER TABLE bots_transactions DROP COLUMN IF EXISTS max_retries;

-- 3. Ajouter les contraintes de validation
ALTER TABLE bots_transactions ADD CONSTRAINT check_bot_num_range 
    CHECK (bot_num >= 1 AND bot_num <= 10);

ALTER TABLE bots_transactions ADD CONSTRAINT check_bot_type_valid 
    CHECK (bot_type IN ('yalla_ludo', 'pubg'));

-- 4. Mettre à jour les valeurs de bot_type si nécessaire
UPDATE bots_transactions SET bot_type = 'pubg' WHERE bot_type IS NULL;

-- 5. Rendre bot_type obligatoire
ALTER TABLE bots_transactions ALTER COLUMN bot_type SET NOT NULL;

-- 6. Mettre à jour les payloads existants pour inclure email et password si manquants
-- (Cette partie dépend de vos données existantes)
UPDATE bots_transactions 
SET payload = payload || '{"email": "default@example.com", "password": "defaultpass"}'::jsonb
WHERE payload IS NOT NULL 
  AND NOT (payload ? 'email' AND payload ? 'password');

-- 7. Vérification finale
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'bots_transactions' 
ORDER BY ordinal_position;

-- 8. Vérifier les contraintes
SELECT 
    conname as constraint_name,
    contype as constraint_type,
    pg_get_constraintdef(oid) as definition
FROM pg_constraint 
WHERE conrelid = 'bots_transactions'::regclass;

