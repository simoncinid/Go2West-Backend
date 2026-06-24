-- Aggiunge la tipologia "esperienze ed escursioni" all'ENUM type della tabella tours.

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
    'esperienze ed escursioni',
    'extra'
) NOT NULL;
