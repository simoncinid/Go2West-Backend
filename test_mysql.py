# Script per testare la connessione al database MySQL

import os
import pymysql
from dotenv import load_dotenv

# Carica le variabili d'ambiente
load_dotenv()

def test_mysql_connection():
    """Testa la connessione al database MySQL"""
    try:
        # Parametri di connessione
        host = os.getenv('DB_HOST', 'db-mysql-fra1-09501-do-user-24280960-0.l.db.ondigitalocean.com')
        port = int(os.getenv('DB_PORT', 25060))
        user = os.getenv('DB_USERNAME', 'doadmin')
        password = os.getenv('DB_PASSWORD', 'AVNS_q6pjJ1Aego6vWH4f1Wk')
        database = os.getenv('DB_NAME', 'defaultdb')
        ssl_cert = os.getenv('DB_CERTIFICATE')
        
        print(f"🔌 Tentativo di connessione a MySQL...")
        print(f"   Host: {host}")
        print(f"   Port: {port}")
        print(f"   User: {user}")
        print(f"   Database: {database}")
        print(f"   SSL Certificate: {'Personalizzato' if ssl_cert else 'Sistema'}")
        
        # Configurazione SSL
        ssl_config = {}
        if ssl_cert:
            # Usa il certificato personalizzato
            ssl_config = {
                'ssl': {
                    'ca': ssl_cert,
                    'check_hostname': False
                }
            }
        else:
            # Usa SSL di default
            ssl_config = {'ssl': {}}
        
        # Connessione al database
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            **ssl_config,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        print("✅ Connessione MySQL riuscita!")
        
        # Test query
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION() as version")
            result = cursor.fetchone()
            print(f"📊 Versione MySQL: {result['version']}")
            
            # Controlla se la tabella tours esiste
            cursor.execute("SHOW TABLES LIKE 'tour'")
            tables = cursor.fetchall()
            
            if tables:
                print("✅ Tabella 'tour' trovata!")
                
                # Conta i record
                cursor.execute("SELECT COUNT(*) as count FROM tour")
                count_result = cursor.fetchone()
                print(f"📊 Numero di tour nel database: {count_result['count']}")
                
                # Mostra alcuni tour
                cursor.execute("SELECT id, title, country, price FROM tour LIMIT 5")
                tours = cursor.fetchall()
                
                if tours:
                    print("📋 Primi 5 tour nel database:")
                    for tour in tours:
                        print(f"   - {tour['title']} ({tour['country']}) - €{tour['price']}")
                else:
                    print("📋 Nessun tour presente nel database")
            else:
                print("⚠️  Tabella 'tour' non trovata. Verrà creata automaticamente dal backend.")
        
        connection.close()
        print("🔌 Connessione chiusa")
        
    except Exception as e:
        print(f"❌ Errore di connessione MySQL: {e}")
        print("\n🔧 Possibili soluzioni:")
        print("   1. Verifica che le credenziali siano corrette")
        print("   2. Controlla che il database sia accessibile dall'IP di Render")
        print("   3. Verifica che SSL sia configurato correttamente")
        print("   4. Controlla che la porta 25060 sia aperta")

def create_test_table():
    """Crea una tabella di test per verificare i permessi"""
    try:
        # Parametri di connessione
        host = os.getenv('DB_HOST', 'db-mysql-fra1-09501-do-user-24280960-0.l.db.ondigitalocean.com')
        port = int(os.getenv('DB_PORT', 25060))
        user = os.getenv('DB_USERNAME', 'doadmin')
        password = os.getenv('DB_PASSWORD', 'AVNS_q6pjJ1Aego6vWH4f1Wk')
        database = os.getenv('DB_NAME', 'defaultdb')
        ssl_cert = os.getenv('DB_CERTIFICATE')
        
        # Configurazione SSL
        ssl_config = {}
        if ssl_cert:
            # Usa il certificato personalizzato
            ssl_config = {
                'ssl': {
                    'ca': ssl_cert,
                    'check_hostname': False
                }
            }
        else:
            # Usa SSL di default
            ssl_config = {'ssl': {}}
        
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            **ssl_config,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # Crea tabella di test
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_connection (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    message VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Inserisci un record di test
            cursor.execute("""
                INSERT INTO test_connection (message) VALUES ('Test connessione riuscita')
            """)
            
            connection.commit()
            print("✅ Tabella di test creata e record inserito con successo!")
            
            # Pulisci la tabella di test
            cursor.execute("DROP TABLE test_connection")
            print("🧹 Tabella di test rimossa")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Errore nella creazione della tabella di test: {e}")

if __name__ == "__main__":
    print("🚀 Test connessione database MySQL")
    print("=" * 50)
    
    # Test connessione
    test_mysql_connection()
    
    print("\n" + "=" * 50)
    
    # Test creazione tabella
    print("🔧 Test permessi database...")
    create_test_table()
    
    print("\n" + "=" * 50)
    print("✅ Test completato!")
