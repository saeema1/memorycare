import sqlite3
import os

db = os.path.join(os.path.dirname(__file__), '..', 'db.sqlite3')
conn = sqlite3.connect(db)
cur = conn.cursor()
try:
    cur.execute("SELECT id, username, first_name, last_name, role FROM users ORDER BY id")
    rows = cur.fetchall()
    print('All users:')
    for r in rows:
        print(r)

    # Check for suspicious values containing template braces or empty names
    print('\nPotentially problematic first/last names (contain {{ or }} or are empty):')
    cur.execute("SELECT id, username, first_name, last_name FROM users WHERE first_name='' OR last_name='' OR first_name LIKE '%{{%' OR last_name LIKE '%{{%' OR first_name LIKE '%}}%' OR last_name LIKE '%}}%'")
    bad = cur.fetchall()
    for b in bad:
        print(b)
    if not bad:
        print('None found')
except Exception as e:
    print('ERROR', e)
finally:
    conn.close()
