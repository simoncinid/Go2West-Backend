-- Aggiunge il campo testuale "fornitore" alla tabella tours
ALTER TABLE tours
ADD COLUMN fornitore VARCHAR(255) NULL AFTER notes;
