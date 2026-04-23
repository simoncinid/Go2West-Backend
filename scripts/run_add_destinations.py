#!/usr/bin/env python3
"""
Converte geographic_area in VARCHAR(100) per evitare "Data truncated" (1265).
Così restano validi tutti i valori esistenti (EST, OVEST, Sud America, ecc.)
e si possono usare HAWAII e ALASKA senza altri ALTER.
Richiede: .env con DB_CERTIFICATE (o variabili DB_*) e pymysql.
Uso: python scripts/run_add_destinations.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pymysql
from dotenv import load_dotenv

load_dotenv()

# VARCHAR accetta qualunque valore; niente più errori 1265 per ENUM
ALTER_SQL = """
ALTER TABLE tours
MODIFY COLUMN geographic_area VARCHAR(100) NULL;
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
        print('OK: geographic_area convertita in VARCHAR(100). HAWAII e ALASKA utilizzabili.')
    except Exception as e:
        print(f'Errore: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()
