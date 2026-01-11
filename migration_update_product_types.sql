-- Migrazione per aggiornare i tipi di prodotto nella tabella tours
-- Data: 2024

-- Step 1: Aggiorna i valori esistenti con le nuove denominazioni
-- Mappatura dei vecchi valori ai nuovi (tutti in minuscolo)

UPDATE tours 
SET type = 'city breaks' 
WHERE type = 'city breaks';

UPDATE tours 
SET type = 'fly & drive' 
WHERE type IN ('fly and drive', 'fly & drive (individuali)');

UPDATE tours 
SET type = 'tour guidato' 
WHERE type IN ('tour guidato', 'tour guidati (di gruppo)');

UPDATE tours 
SET type = 'camper adventure' 
WHERE type IN ('camper adventure', 'camper adventures');

UPDATE tours 
SET type = 'glamping' 
WHERE type IN ('Glamping usa', 'under canvas usa', 'glamping');

UPDATE tours 
SET type = 'ranch' 
WHERE type = 'ranch usa e canada';

UPDATE tours 
SET type = 'scoperta in treno' 
WHERE type = 'scoperta in treno';

UPDATE tours 
SET type = 'hotel/resort' 
WHERE type = 'hotel/resort';

UPDATE tours 
SET type = 'luxury travel' 
WHERE type = 'luxury travel';

UPDATE tours 
SET type = 'extra' 
WHERE type IN ('extra', 'ride in harley');

-- Step 2: Modifica la colonna type per usare il nuovo ENUM
-- Nota: MySQL richiede di modificare la colonna dopo aver aggiornato i valori

ALTER TABLE tours 
MODIFY COLUMN type ENUM(
    'city breaks',
    'fly & drive',
    'tour guidato',
    'camper adventure',
    'glamping',
    'ranch',
    'scoperta in treno',
    'hotel/resort',
    'combinati',
    'luxury travel',
    'extra'
) NOT NULL;

-- Verifica: Controlla che tutti i tour abbiano un tipo valido
-- SELECT type, COUNT(*) as count FROM tours GROUP BY type;
