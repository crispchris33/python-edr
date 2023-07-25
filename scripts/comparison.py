#this script will compare the object db in the user_config.json to the nist db of known files
#existing hash values are sha256, sha1, md5

import sqlite3

conn = sqlite3.connect('D:\Hashing DB\RDS_2023.06.1_modern_minimal.db')
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS comparison_event (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        start_date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

try:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS match_found (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_name TEXT UNIQUE,
        file_size INTEGER,
        md5 VARCHAR,
        sha1 VARCHAR,
        sha256 VARCHAR,
        event_id INTEGER,
        date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

except Exception as e:
    print(e)

cursor.execute("INSERT INTO comparison_event DEFAULT VALUES")
event_id = cursor.lastrowid

print("Starting md5 comparison...")
cursor.execute(f"""
    INSERT OR IGNORE INTO match_found (file_name, file_size, md5, event_id)
    SELECT f.file_name,
           f.file_size,
           f.md5,
           {event_id}
    FROM FILE f
    JOIN scanned_file s ON f.md5 = s.md5
""")

cursor.execute(f"""
    UPDATE match_found
    SET md5 = (SELECT f.md5 FROM FILE f JOIN scanned_file s ON f.md5 = s.md5 WHERE match_found.file_name = f.file_name),
        event_id = {event_id}
    WHERE match_found.file_name IN (SELECT f.file_name FROM FILE f JOIN scanned_file s ON f.md5 = s.md5)
""")
conn.commit()

print("Starting sha1 comparison...")
cursor.execute(f"""
    INSERT OR IGNORE INTO match_found (file_name, file_size, sha1, event_id)
    SELECT f.file_name,
           f.file_size,
           f.sha1,
           {event_id}
    FROM FILE f
    JOIN scanned_file s ON f.sha1 = s.sha1
""")

cursor.execute(f"""
    UPDATE match_found
    SET sha1 = (SELECT f.sha1 FROM FILE f JOIN scanned_file s ON f.sha1 = s.sha1 WHERE match_found.file_name = f.file_name),
        event_id = {event_id}
    WHERE match_found.file_name IN (SELECT f.file_name FROM FILE f JOIN scanned_file s ON f.sha1 = s.sha1)
""")
conn.commit()

print("Starting sha256 comparison...")
cursor.execute(f"""
    INSERT OR IGNORE INTO match_found (file_name, file_size, sha256, event_id)
    SELECT f.file_name,
           f.file_size,
           f.sha256,
           {event_id}
    FROM FILE f
    JOIN scanned_file s ON f.sha256 = s.sha256
""")

cursor.execute(f"""
    UPDATE match_found
    SET sha256 = (SELECT f.sha256 FROM FILE f JOIN scanned_file s ON f.sha256 = s.sha256 WHERE match_found.file_name = f.file_name),
        event_id = {event_id}
    WHERE match_found.file_name IN (SELECT f.file_name FROM FILE f JOIN scanned_file s ON f.sha256 = s.sha256)
""")
conn.commit()

conn.close()