-- Aggiungi campo category_type alla tabella user_categories
ALTER TABLE user_categories 
ADD COLUMN category_type VARCHAR(10) DEFAULT 'expense' AFTER color;

-- Aggiorna le categorie esistenti a 'expense'
UPDATE user_categories SET category_type = 'expense' WHERE category_type IS NULL;



