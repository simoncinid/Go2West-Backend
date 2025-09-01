# Script per Inserimento Dati nel Database

Questo repository contiene script Python per inserire direttamente i dati di test nel database MySQL senza passare dall'API Flask.

## File Disponibili

### 1. `insert_data_direct.py` (Base)
Script base per inserire 5 tour di esempio nel database.

**Caratteristiche:**
- Inserisce 5 tour predefiniti
- Configurazione SSL semplificata
- Verifica automatica dei dati inseriti

### 2. `insert_data_direct_enhanced.py` (Avanzato)
Script avanzato con funzionalità aggiuntive.

**Caratteristiche:**
- Inserisce 8 tour di esempio
- Opzione per svuotare la tabella esistente
- Statistiche dettagliate del database
- Verifica dell'integrità dei dati
- Interfaccia interattiva

## Configurazione del Database

Gli script utilizzano la seguente configurazione hardcoded:

```python
username = 'doadmin'
password = 'AVNS_q6pjJ1Aego6vWH4f1Wk'
host = 'db-mysql-fra1-09501-do-user-24280960-0.l.db.ondigitalocean.com'
port = 25060
database = 'defaultdb'
```

## Prerequisiti

Assicurati di avere installato le dipendenze Python:

```bash
pip install -r requirements.txt
```

## Utilizzo

### Script Base
```bash
python insert_data_direct.py
```

### Script Avanzato
```bash
python insert_data_direct_enhanced.py
```

Lo script avanzato ti chiederà se vuoi svuotare la tabella esistente prima di inserire i nuovi dati.

## Struttura della Tabella

La tabella `tour` viene creata automaticamente con la seguente struttura:

```sql
CREATE TABLE tour (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titolo VARCHAR(200) NOT NULL,
    paese VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    prezzo FLOAT NOT NULL,
    durata INT,
    descrizione TEXT,
    immagine_principale VARCHAR(500),
    immagini TEXT,
    punti_salienti TEXT,
    itinerario TEXT,
    incluso TEXT,
    non_incluso TEXT,
    note TEXT,
    data_creazione DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_aggiornamento DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

## Tour Inclusi

### Script Base (5 tour):
1. **Tour del Giappone Classico** - €2.499
2. **Safari in Kenya** - €1.899
3. **Fly & Drive Stati Uniti** - €1.599
4. **Crociera Messico e Caraibi** - €1.299
5. **Avventura in Australia** - €2.899

### Script Avanzato (8 tour):
Tutti i tour del script base più:
6. **Tour dell'Argentina** - €2.199
7. **Crociera Polinesia** - €3.499
8. **Tour in Harley Davidson** - €3.999

## Gestione degli Errori

Gli script includono:
- Gestione degli errori di connessione
- Rollback automatico in caso di errori di inserimento
- Messaggi informativi dettagliati
- Chiusura automatica delle connessioni

## Note Importanti

- Gli script utilizzano SSL per la connessione al database
- Le immagini sono riferite ai file presenti nella cartella `public/images/`
- I dati sono hardcoded per garantire la funzionalità
- Gli script sono progettati per essere eseguiti in ambiente di sviluppo/test

## Troubleshooting

### Errore di Connessione SSL
Se riscontri problemi con SSL, lo script utilizza una configurazione semplificata che dovrebbe funzionare con la maggior parte dei database MySQL.

### Errore di Duplicazione
Se esegui lo script più volte, potresti ricevere errori di duplicazione per i campi `slug` che sono unici. Usa lo script avanzato e scegli di svuotare la tabella.

### Dipendenze Mancanti
Assicurati di aver installato tutte le dipendenze:
```bash
pip install pymysql python-dotenv
```
