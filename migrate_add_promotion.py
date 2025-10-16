#!/usr/bin/env python3
"""
Script di migrazione per aggiungere il campo is_promotion alla tabella tours
"""

import os
import sys
import tempfile
from dotenv import load_dotenv
import pymysql

# Registra PyMySQL come driver MySQL
pymysql.install_as_MySQLdb()

# Carica le variabili d'ambiente
load_dotenv()

def create_ssl_cert_file():
    """Crea un file temporaneo con il certificato SSL dalla variabile d'ambiente"""
    ssl_cert_content = os.environ.get('DB_CERTIFICATE')
    
    if not ssl_cert_content:
        print("Variabile d'ambiente DB_CERTIFICATE non trovata")
        return None
    
    try:
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.crt', delete=False)
        temp_file.write(ssl_cert_content)
        temp_file.close()
        return temp_file.name
    except Exception as e:
        print(f"Errore nella creazione del file certificato: {e}")
        return None

def get_database_connection():
    """Crea una connessione al database"""
    username = 'doadmin'
    password = 'AVNS_q6pjJ1Aego6vWH4f1Wk'
    host = 'db-mysql-fra1-09501-do-user-24280960-0.l.db.ondigitalocean.com'
    port = 25060
    database = 'defaultdb'
    
    ssl_cert_path = create_ssl_cert_file()
    
    try:
        if ssl_cert_path:
            connection = pymysql.connect(
                host=host,
                port=port,
                user=username,
                password=password,
                database=database,
                charset='utf8mb4',
                ssl_ca=ssl_cert_path,
                ssl_verify_cert=True,
                ssl_verify_identity=True
            )
        else:
            connection = pymysql.connect(
                host=host,
                port=port,
                user=username,
                password=password,
                database=database,
                charset='utf8mb4',
                ssl={'ssl_mode': 'REQUIRED'}
            )
        
        return connection
    except Exception as e:
        print(f"Errore nella connessione al database: {e}")
        return None

def migrate_add_promotion_field():
    """Aggiunge il campo is_promotion alla tabella tours"""
    connection = get_database_connection()
    
    if not connection:
        print("Impossibile connettersi al database")
        return False
    
    try:
        cursor = connection.cursor()
        
        # Controlla se la colonna esiste già
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'defaultdb' 
            AND TABLE_NAME = 'tours' 
            AND COLUMN_NAME = 'is_promotion'
        """)
        
        column_exists = cursor.fetchone()[0] > 0
        
        if column_exists:
            print("La colonna 'is_promotion' esiste già nella tabella 'tours'")
            return True
        
        # Aggiungi la colonna is_promotion
        print("Aggiunta della colonna 'is_promotion' alla tabella 'tours'...")
        cursor.execute("""
            ALTER TABLE tours 
            ADD COLUMN is_promotion BOOLEAN DEFAULT FALSE COMMENT 'Indica se il tour è in promozione'
        """)
        
        # Crea l'indice per migliorare le performance
        print("Creazione dell'indice per la colonna 'is_promotion'...")
        cursor.execute("""
            CREATE INDEX idx_tours_is_promotion ON tours(is_promotion)
        """)
        
        connection.commit()
        print("✅ Migrazione completata con successo!")
        
        # Verifica che la colonna sia stata aggiunta
        cursor.execute("DESCRIBE tours")
        columns = cursor.fetchall()
        
        print("\nStruttura aggiornata della tabella 'tours':")
        for column in columns:
            print(f"  - {column[0]}: {column[1]} {column[2]} {column[3]} {column[4]} {column[5]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore durante la migrazione: {e}")
        connection.rollback()
        return False
    
    finally:
        connection.close()

if __name__ == "__main__":
    print("🚀 Avvio migrazione database per aggiungere il campo 'is_promotion'...")
    success = migrate_add_promotion_field()
    
    if success:
        print("\n🎉 Migrazione completata! Ora puoi utilizzare le funzionalità di promozione.")
        sys.exit(0)
    else:
        print("\n💥 Migrazione fallita. Controlla i log per maggiori dettagli.")
        sys.exit(1)
