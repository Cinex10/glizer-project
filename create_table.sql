-- Script SQL pour créer la table bots_transactions
-- Architecture simplifiée selon les spécifications Salla

CREATE TABLE IF NOT EXISTS bots_transactions (
    id VARCHAR PRIMARY KEY,
    bot_num INTEGER NOT NULL CHECK (bot_num >= 1 AND bot_num <= 10),
    status VARCHAR DEFAULT 'pending',
    payload JSONB,
    bot_type VARCHAR NOT NULL CHECK (bot_type IN ('yalla_ludo', 'pubg'))
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_bots_transactions_bot_num ON bots_transactions(bot_num);
CREATE INDEX IF NOT EXISTS idx_bots_transactions_status ON bots_transactions(status);
CREATE INDEX IF NOT EXISTS idx_bots_transactions_bot_type ON bots_transactions(bot_type);

-- Exemple d'insertion de données de test avec la nouvelle structure de payload
-- Note: email/password stockés dans la base mais utilisent les credentials rotatifs pour l'automatisation
INSERT INTO bots_transactions (id, bot_num, status, payload, bot_type) VALUES
('test-transaction-1', 9, 'pending', '{"player_id": "533938203", "code": "TESTCODE1", "email": "test@example.com", "password": "testpass"}', 'pubg'),
('test-transaction-2', 10, 'pending', '{"player_id": "987654321", "code": "EXAMPLE123", "email": "user@example.com", "password": "userpass"}', 'pubg'),
('test-transaction-3', 5, 'pending', '{"player_id": "123456789", "code": "YALLACODE", "email": "yalla@example.com", "password": "yallapass"}', 'yalla_ludo')
ON CONFLICT (id) DO NOTHING;

-- Vérification
SELECT * FROM bots_transactions ORDER BY bot_num;


