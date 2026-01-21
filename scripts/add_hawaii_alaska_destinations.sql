-- Aggiunge HAWAII e ALASKA alle zone USA (geographic_area) insieme a EST, OVEST, SOUTH, ecc.
-- Eseguire solo se la colonna geographic_area è di tipo ENUM.
-- Se è VARCHAR/TEXT non serve: i valori sono già accettati.

ALTER TABLE tours
MODIFY COLUMN geographic_area ENUM(
  'EST',
  'OVEST',
  'EST E OVEST',
  'SOUTH',
  'MID WEST',
  'HAWAII',
  'ALASKA'
) NULL;
