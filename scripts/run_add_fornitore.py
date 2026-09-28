#!/usr/bin/env python3
"""
Aggiunge la colonna fornitore alla tabella tours.
Richiede: .env con variabili DB_* e pymysql.
Uso: python scripts/run_add_fornitore.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pymysql
from dotenv import load_dotenv

load_dotenv()

ALTER_SQL = """
ALTER TABLE tours
ADD COLUMN fornitore VARCHAR(255) NULL AFTER notes;
"""


def main():
    host = os.getenv('DB_HOST')
    port = int(os.getenv('DB_PORT', 25060))
    user = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD')
    database = os.getenv('DB_NAME')
    ssl_cert = os.getenv('DB_CERTIFICATE')

    if not all([host, user, password, database]):
        print('Errore: imposta DB_HOST, DB_USERNAME, DB_PASSWORD e DB_NAME nel .env')
        sys.exit(1)

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
        print('OK: colonna fornitore aggiunta alla tabella tours.')
    except Exception as e:
        if 'Duplicate column name' in str(e):
            print('OK: la colonna fornitore esiste già.')
            return
        print(f'Errore: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
