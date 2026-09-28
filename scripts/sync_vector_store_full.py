#!/usr/bin/env python3
"""Sincronizza TUTTI i tour nel vector store OpenAI con filename corretti e LINK TOUR."""

import os
import re
import sys
import tempfile
from datetime import datetime

import pymysql
from openai import OpenAI

VECTOR_STORE_ID = "vs_68f350c542d88191a4026139f8bae406"
TOUR_PUBLIC_URL_TEMPLATE = "https://www.go2west.org/tour/{code}"

DB_CONFIG = {
    "host": os.environ["DB_HOST"],
    "port": int(os.environ.get("DB_PORT", "25060")),
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASSWORD"],
    "database": os.environ.get("DB_NAME", "defaultdb"),
    "charset": "utf8mb4",
    "ssl": {"ssl": {}},
    "cursorclass": pymysql.cursors.DictCursor,
}


def build_tour_public_url(tour_code):
    if not tour_code:
        return None
    return TOUR_PUBLIC_URL_TEMPLATE.format(code=tour_code)


def generate_tour_txt_content(tour):
    tour_link = build_tour_public_url(tour.get("code"))
    content = f"""TOUR: {tour.get('title')}
CODICE: {tour.get('code')}
DESTINAZIONE: {tour.get('destination')}
TIPO DI VIAGGIO: {tour.get('type')}
DURATA: {tour.get('duration')} giorni
PREZZO MINIMO: €{tour.get('minPrice') if tour.get('minPrice') else 'Da definire'}
LINK TOUR: {tour_link if tour_link else 'Non disponibile'}

DESCRIZIONE:
{tour.get('description') or 'Nessuna descrizione disponibile'}

"""

    program = tour.get("program")
    if program:
        content += "PROGRAMMA DI VIAGGIO:\n"
        if isinstance(program, (list, tuple)):
            for i, day in enumerate(program, 1):
                if isinstance(day, dict):
                    content += f"Giorno {i}: {day.get('title', '')}\n"
                    content += f"{day.get('description', '')}\n\n"
                else:
                    content += f"Giorno {i}: {day}\n\n"
        else:
            content += f"{program}\n\n"

    if tour.get("itinerario"):
        content += f"ITINERARIO:\n{tour.get('itinerario')}\n\n"

    prices = tour.get("prices")
    if prices:
        content += "PREZZI:\n"
        if isinstance(prices, list):
            for price in prices:
                if isinstance(price, dict):
                    content += f"- {price.get('category', '')}: €{price.get('price', '')}\n"
                else:
                    content += f"- {price}\n"
        else:
            content += f"{prices}\n"
        content += "\n"

    included = tour.get("included")
    if included:
        content += "INCLUSO NEL PREZZO:\n"
        if isinstance(included, list):
            for item in included:
                content += f"- {item}\n"
        else:
            content += f"{included}\n"
        content += "\n"

    not_included = tour.get("notIncluded")
    if not_included:
        content += "NON INCLUSO NEL PREZZO:\n"
        if isinstance(not_included, list):
            for item in not_included:
                content += f"- {item}\n"
        else:
            content += f"{not_included}\n"
        content += "\n"

    if tour.get("pasti"):
        content += f"PASTI:\n{tour.get('pasti')}\n\n"

    dates = tour.get("dates")
    if dates:
        content += "DATE DISPONIBILI:\n"
        if isinstance(dates, list):
            for date in dates:
                content += f"- {date}\n"
        else:
            content += f"{dates}\n"
        content += "\n"

    if tour.get("notes"):
        content += f"NOTE AGGIUNTIVE:\n{tour.get('notes')}\n\n"

    if tour.get("is_promotion"):
        content += "QUESTO TOUR È ATTUALMENTE IN PROMOZIONE!\n\n"

    created_at = tour.get("created_at")
    updated_at = tour.get("updated_at")
    content += f"Creato il: {created_at.strftime('%d/%m/%Y') if created_at else 'N/A'}\n"
    content += f"Ultimo aggiornamento: {updated_at.strftime('%d/%m/%Y') if updated_at else 'N/A'}\n"
    return content


def parse_json_fields(tour):
    import json

    for key in ("program", "prices", "included", "notIncluded", "dates"):
        value = tour.get(key)
        if isinstance(value, str) and value.strip():
            try:
                tour[key] = json.loads(value)
            except Exception:
                pass
    return tour


def list_vs_files(client):
    files = []
    after = None
    while True:
        kwargs = {"vector_store_id": VECTOR_STORE_ID, "limit": 100}
        if after:
            kwargs["after"] = after
        page = client.vector_stores.files.list(**kwargs)
        files.extend(page.data)
        if not getattr(page, "has_more", False) or not page.data:
            break
        after = page.data[-1].id
    return files


def upsert_tour_file(conn, tour_id, filename, file_id):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM tour_files WHERE tour_id=%s", (tour_id,))
        row = cur.fetchone()
        now = datetime.utcnow()
        if row:
            cur.execute(
                "UPDATE tour_files SET filename=%s, vector_store_file_id=%s, updated_at=%s WHERE tour_id=%s",
                (filename, file_id, now, tour_id),
            )
        else:
            cur.execute(
                "INSERT INTO tour_files (tour_id, filename, vector_store_file_id, created_at, updated_at) VALUES (%s,%s,%s,%s,%s)",
                (tour_id, filename, file_id, now, now),
            )
    conn.commit()


def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY mancante")
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    conn = pymysql.connect(**DB_CONFIG)

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, code, title, destination, type, duration, minPrice, description,
                       program, itinerario, prices, included, notIncluded, pasti, dates, notes,
                       is_promotion, created_at, updated_at
                FROM tours
                ORDER BY id
                """
            )
            tours = [parse_json_fields(t) for t in cur.fetchall()]

            cur.execute("SELECT tour_id, vector_store_file_id FROM tour_files")
            existing = {r["tour_id"]: r["vector_store_file_id"] for r in cur.fetchall()}

        print(f"Tour in DB: {len(tours)}")
        print(f"Record tour_files: {len(existing)}")

        tracked_ids = set()
        success = 0
        errors = 0

        for idx, tour in enumerate(tours, 1):
            tour_id = tour["id"]
            filename = f"tour_{tour_id}_{tour['code']}.txt"
            old_file_id = existing.get(tour_id)

            try:
                if old_file_id:
                    try:
                        client.vector_stores.files.delete(
                            vector_store_id=VECTOR_STORE_ID, file_id=old_file_id
                        )
                    except Exception as e:
                        print(f"  warn remove vs {tour_id}: {e}")
                    try:
                        client.files.delete(old_file_id)
                    except Exception:
                        pass

                content = generate_tour_txt_content(tour)
                temp_dir = tempfile.mkdtemp()
                temp_path = os.path.join(temp_dir, filename)
                with open(temp_path, "w", encoding="utf-8") as f:
                    f.write(content)

                try:
                    with open(temp_path, "rb") as f:
                        uploaded = client.files.create(
                            file=(filename, f),
                            purpose="assistants",
                        )
                    client.vector_stores.files.create(
                        vector_store_id=VECTOR_STORE_ID,
                        file_id=uploaded.id,
                    )
                    upsert_tour_file(conn, tour_id, filename, uploaded.id)
                    tracked_ids.add(uploaded.id)
                    success += 1
                    print(f"[{idx}/{len(tours)}] OK tour {tour_id} -> {uploaded.id}")
                finally:
                    try:
                        os.unlink(temp_path)
                    except OSError:
                        pass
                    try:
                        os.rmdir(temp_dir)
                    except OSError:
                        pass
            except Exception as e:
                errors += 1
                print(f"[{idx}/{len(tours)}] ERR tour {tour_id}: {e}")

        # Cleanup orphan VS files
        print("Cleanup orfani...")
        removed = 0
        for vs_file in list_vs_files(client):
            if vs_file.id in tracked_ids:
                continue
            try:
                client.vector_stores.files.delete(
                    vector_store_id=VECTOR_STORE_ID, file_id=vs_file.id
                )
                try:
                    client.files.delete(vs_file.id)
                except Exception:
                    pass
                removed += 1
            except Exception as e:
                print(f"  orphan err {vs_file.id}: {e}")

        # Verify filenames
        named_ok = 0
        tmp_left = 0
        for vs_file in list_vs_files(client):
            try:
                meta = client.files.retrieve(vs_file.id)
                name = meta.filename or ""
            except Exception:
                name = ""
            if re.match(r"^tour_\d+_.+\.txt$", name):
                named_ok += 1
            elif name.startswith("tmp"):
                tmp_left += 1

        print("---")
        print(f"success={success} errors={errors} orphans_removed={removed}")
        print(f"named_ok={named_ok} tmp_left={tmp_left}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
