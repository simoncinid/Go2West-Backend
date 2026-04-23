-- Fix per "Data truncated" (1265): geographic_area conteneva valori
-- non nell'ENUM (es. Sud America, Nord America, stringa vuota, ecc.).
--
-- Soluzione: convertire a VARCHAR(100) così tutti i valori esistenti
-- restano validi e si possono usare HAWAII, ALASKA e le zone USA
-- (EST, OVEST, SOUTH, MID WEST, EST E OVEST) senza altri ALTER.
-- Il modello in app.py è già String(100).

ALTER TABLE tours
MODIFY COLUMN geographic_area VARCHAR(100) NULL;
