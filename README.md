# Go2West Backend API

Backend Python Flask per l'API di Go2West Travel.

## Funzionalità

- **Gestione Tour**: CRUD completo per i tour di viaggio
- **Autenticazione**: Sistema di autenticazione per l'admin panel
- **Database**: Supporto per PostgreSQL (produzione) e SQLite (sviluppo)
- **CORS**: Configurato per permettere richieste dal frontend React

## Struttura del Database

### Tabella Tour
- `id`: ID univoco del tour
- `title`: Titolo del tour
- `country`: Paese di destinazione
- `type`: Tipo di tour (tour, fly-drive, safari, cruise, adventure)
- `slug`: URL slug univoco
- `price`: Prezzo in euro
- `duration`: Durata in giorni
- `description`: Descrizione del tour
- `mainImage`: URL dell'immagine principale
- `images`: Array di URL delle immagini (salvato come stringa)
- `highlights`: Array dei punti salienti (salvato come stringa)
- `itinerary`: Array dell'itinerario (salvato come stringa)
- `included`: Array dei servizi inclusi (salvato come stringa)
- `notIncluded`: Array dei servizi non inclusi (salvato come stringa)
- `notes`: Note aggiuntive
- `created_at`: Data di creazione
- `updated_at`: Data di ultimo aggiornamento

## API Endpoints

### Tour
- `GET /api/tours` - Ottieni tutti i tour
- `GET /api/tours/<id>` - Ottieni un tour specifico
- `POST /api/tours` - Crea un nuovo tour
- `PUT /api/tours/<id>` - Aggiorna un tour
- `DELETE /api/tours/<id>` - Elimina un tour

### Filtri
- `GET /api/tours/country/<country>` - Tour per paese
- `GET /api/tours/type/<type>` - Tour per tipo
- `GET /api/tours/slug/<slug>` - Tour per slug

### Utility
- `GET /health` - Health check per Render
- `GET /` - Informazioni API

## Installazione Locale

1. **Clona il repository**
```bash
git clone <repository-url>
cd go2west-backend
```

2. **Crea un ambiente virtuale**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oppure
venv\Scripts\activate  # Windows
```

3. **Installa le dipendenze**
```bash
pip install -r requirements.txt
```

4. **Configura le variabili d'ambiente**
Crea un file `.env` nella root del progetto:
```env
DATABASE_URL=sqlite:///tours.db
PORT=5000
FLASK_ENV=development
```

5. **Avvia il server**
```bash
python app.py
```

Il server sarà disponibile su `http://localhost:5000`

## Deploy su Render.com

1. **Crea un nuovo Web Service su Render**
2. **Connetti il repository GitHub**
3. **Configura le variabili d'ambiente**:
   - `DATABASE_URL`: URL del database PostgreSQL di Render
   - `PORT`: 10000 (porta standard di Render)
4. **Build Command**: `pip install -r requirements.txt`
5. **Start Command**: `gunicorn app:app`

## Variabili d'Ambiente

### Sviluppo Locale
- `DATABASE_URL`: URL del database SQLite
- `PORT`: Porta del server (default: 5000)
- `FLASK_ENV`: Ambiente Flask (development/production)

### Produzione (Render)
- `DATABASE_URL`: URL del database PostgreSQL di Render
- `PORT`: Porta del server (default: 10000)

## Esempio di Richiesta API

### Creare un nuovo tour
```bash
curl -X POST http://localhost:5000/api/tours \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Tour del Giappone",
    "country": "Giappone",
    "type": "tour",
    "slug": "tour-giappone-2024",
    "price": 2500.00,
    "duration": 10,
    "description": "Un fantastico tour del Giappone",
    "mainImage": "https://example.com/japan.jpg"
  }'
```

### Ottenere tutti i tour
```bash
curl http://localhost:5000/api/tours
```

## Note per lo Sviluppo

- Il database viene creato automaticamente al primo avvio
- Le immagini sono salvate come URL (non file fisici)
- Gli array sono salvati come stringhe separate da virgole nel database
- CORS è configurato per permettere richieste da `http://localhost:3000` (frontend React)
- Il server usa Gunicorn in produzione per migliori performance
