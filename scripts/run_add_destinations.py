#!/usr/bin/env python3
"""
Esegue l'ALTER sulla tabella tours per aggiungere Hawaii e Alaska alla colonna destination.
Richiede: .env con DB_CERTIFICATE (o variabili DB_*) e pymysql.
Uso: python scripts/run_add_destinations.py
"""
import os
import sys

# Aggiungi la root del progetto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pymysql
from dotenv import load_dotenv

load_dotenv()

ALTER_SQL = """
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
"""

def main():
    host = os.getenv('DB_HOST', 'db-mysql-fra1-09501-do-user-24280960-0.l.db.ondigitalocean.com')
    port = int(os.getenv('DB_PORT', 25060))
    user = os.getenv('DB_USERNAME', 'doadmin')
    password = os.getenv('DB_PASSWORD', 'AVNS_q6pjJ1Aego6vWH4f1Wk')
    database = os.getenv('DB_NAME', 'defaultdb')
    ssl_cert = os.getenv('DB_CERTIFICATE')

    ssl_config = {'ssl': {'ca': ssl_cert, 'check_hostname': False}} if ssl_cert else {'ssl': {}}

    try:
        conn = pymysql.connect(
            host=host, port=port, user=user, password=password, database=database,
            **ssl_config, charset='utf8mb4'
        )
        with conn.cursor() as cur:
            cur.execute(ALTER_SQL)
        conn.commit()
        conn.close()
        print('OK: Colonne Hawaii e Alaska aggiunte a destination.')
    except Exception as e:
        print(f'Errore: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()
