-- Aggiungi campo transaction_type alla tabella transactions
ALTER TABLE transactions 
ADD COLUMN transaction_type VARCHAR(20) DEFAULT 'expense' AFTER amount;

-- Aggiorna le transazioni esistenti a 'expense'
UPDATE transactions SET transaction_type = 'expense' WHERE transaction_type IS NULL;



