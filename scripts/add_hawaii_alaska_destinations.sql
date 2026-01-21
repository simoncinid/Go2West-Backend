-- Aggiunge Hawaii e Alaska come destinazioni (stesso livello di USA, Canada, ecc.)
-- Eseguire sul database: defaultdb, tabella: tours

-- Modifica la colonna destination per includere 'Hawaii' e 'Alaska'
ALTER TABLE tours
MODIFY COLUMN destination ENUM(
  'USA',
  'Hawaii',
  'Alaska',
  'Canada',
  'Messico',
  'America Centrale',
  'Sud America',
  'Caraibi',
  'Polinesia Francese'
) NOT NULL;
