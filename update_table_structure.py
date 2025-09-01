# Script per aggiornare la struttura della tabella tour con nomi italiani
import pymysql

def update_table_structure():
    """Aggiorna la struttura della tabella tour per usare nomi italiani"""
    try:
        # Parametri di connessione diretti
        host = 'db-mysql-fra1-09501-do-user-24280960-0.l.db.ondigitalocean.com'
        port = 25060
        user = 'doadmin'
        password = 'AVNS_q6pjJ1Aego6vWH4f1Wk'
        database = 'defaultdb'
        
        print("🔌 Connessione al database MySQL...")
        
        # Connessione al database
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        print("✅ Connessione MySQL riuscita!")
        
        with connection.cursor() as cursor:
            # Controlla la struttura attuale
            cursor.execute("DESCRIBE tour")
            columns = cursor.fetchall()
            
            print("📋 Struttura attuale della tabella 'tour':")
            for col in columns:
                print(f"   - {col['Field']}: {col['Type']}")
            
            # Controlla se le colonne italiane esistono già
            italian_columns = ['titolo', 'paese', 'tipo', 'prezzo', 'durata', 'descrizione', 
                             'immagine_principale', 'immagini', 'punti_salienti', 'itinerario', 
                             'incluso', 'non_incluso', 'note', 'data_creazione', 'data_aggiornamento']
            
            existing_columns = [col['Field'] for col in columns]
            
            if all(col in existing_columns for col in italian_columns):
                print("✅ La tabella ha già i nomi italiani delle colonne!")
                return
            
            # Se non esistono, ricrea la tabella
            print("🔄 Ricreazione della tabella con nomi italiani...")
            
            # Elimina la tabella esistente
            cursor.execute("DROP TABLE IF EXISTS tour")
            
            # Crea la nuova tabella con nomi italiani
            create_table_sql = """
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
                data_creazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_aggiornamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_paese (paese),
                INDEX idx_tipo (tipo),
                INDEX idx_slug (slug)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            cursor.execute(create_table_sql)
            connection.commit()
            
            print("✅ Tabella 'tour' ricreata con nomi italiani!")
            
            # Mostra la nuova struttura
            cursor.execute("DESCRIBE tour")
            new_columns = cursor.fetchall()
            print("📋 Nuova struttura della tabella 'tour':")
            for col in new_columns:
                print(f"   - {col['Field']}: {col['Type']}")
        
        connection.close()
        print("🔌 Connessione chiusa")
        
    except Exception as e:
        print(f"❌ Errore durante l'aggiornamento: {e}")

if __name__ == "__main__":
    print("🔄 Aggiornamento struttura tabella tour")
    print("=" * 50)
    update_table_structure()
    print("=" * 50)
    print("✅ Aggiornamento completato!")
