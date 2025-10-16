#!/usr/bin/env python3
"""
Script di migrazione per aggiungere i campi 'itinerario' e 'pasti' alla tabella tours
"""

import os
import sys
from dotenv import load_dotenv
import pymysql

# Carica le variabili d'ambiente
load_dotenv()

def get_database_connection():
    """Crea una connessione al database MySQL"""
    try:
        # Configurazione del database
        connection = pymysql.connect(
            host='db-mysql-fra1-09501-do-user-24280960-0.l.db.ondigitalocean.com',
            port=25060,
            user='doadmin',
            password='AVNS_q6pjJ1Aego6vWH4f1Wk',
            database='defaultdb',
            charset='utf8mb4',
            ssl_disabled=False
        )
        return connection
    except Exception as e:
        print(f"Errore nella connessione al database: {e}")
        return None

def check_column_exists(cursor, table_name, column_name):
    """Controlla se una colonna esiste già nella tabella"""
    try:
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'defaultdb' 
            AND TABLE_NAME = '{table_name}' 
            AND COLUMN_NAME = '{column_name}'
        """)
        result = cursor.fetchone()
        return result[0] > 0
    except Exception as e:
        print(f"Errore nel controllo della colonna {column_name}: {e}")
        return False

def add_columns():
    """Aggiunge i campi itinerario e pasti alla tabella tours"""
    connection = get_database_connection()
    if not connection:
        print("Impossibile connettersi al database")
        return False
    
    try:
        cursor = connection.cursor()
        
        # Controlla se i campi esistono già
        pasti_exists = check_column_exists(cursor, 'tours', 'pasti')
        itinerario_exists = check_column_exists(cursor, 'tours', 'itinerario')
        
        print(f"Stato attuale:")
        print(f"- Campo 'pasti': {'ESISTE' if pasti_exists else 'NON ESISTE'}")
        print(f"- Campo 'itinerario': {'ESISTE' if itinerario_exists else 'NON ESISTE'}")
        
        # Aggiungi il campo 'pasti' se non esiste
        if not pasti_exists:
            print("\nAggiungendo il campo 'pasti'...")
            cursor.execute("ALTER TABLE tours ADD COLUMN pasti TEXT")
            print("✓ Campo 'pasti' aggiunto con successo")
        else:
            print("✓ Campo 'pasti' già esistente")
        
        # Aggiungi il campo 'itinerario' se non esiste
        if not itinerario_exists:
            print("\nAggiungendo il campo 'itinerario'...")
            cursor.execute("ALTER TABLE tours ADD COLUMN itinerario TEXT")
            print("✓ Campo 'itinerario' aggiunto con successo")
        else:
            print("✓ Campo 'itinerario' già esistente")
        
        # Conferma le modifiche
        connection.commit()
        print("\n🎉 Migrazione completata con successo!")
        
        # Verifica finale
        print("\nVerifica finale della struttura della tabella:")
        cursor.execute("DESCRIBE tours")
        columns = cursor.fetchall()
        
        for column in columns:
            if column[0] in ['pasti', 'itinerario']:
                print(f"- {column[0]}: {column[1]} ({'NULL' if column[2] == 'YES' else 'NOT NULL'})")
        
        return True
        
    except Exception as e:
        print(f"Errore durante la migrazione: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()

def main():
    """Funzione principale"""
    print("=== Migrazione Database: Aggiunta campi itinerario e pasti ===\n")
    
    # Chiedi conferma all'utente
    response = input("Vuoi procedere con l'aggiunta dei campi 'itinerario' e 'pasti'? (s/n): ")
    if response.lower() not in ['s', 'si', 'y', 'yes']:
        print("Migrazione annullata.")
        return
    
    success = add_columns()
    
    if success:
        print("\n✅ La migrazione è stata completata con successo!")
        print("I campi 'itinerario' e 'pasti' sono ora disponibili nella tabella 'tours'.")
    else:
        print("\n❌ La migrazione è fallita. Controlla i log per i dettagli.")
        sys.exit(1)

if __name__ == "__main__":
    main()
