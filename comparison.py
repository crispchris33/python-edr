import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('D:\\Hashing DB\\RDS_2023.06.1_modern_minimal.db')
cursor = conn.cursor()

# Create comparison_matches table if it does not exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS comparison_matches (
        match_id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_name_nist TEXT,
        sha256_nist TEXT,
        sha1_nist TEXT,
        md5_nist TEXT,
        file_name_local TEXT,
        sha256_local TEXT,
        sha1_local TEXT,
        md5_local TEXT,
        date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Fill comparison_matches table with matching entries from FILE and scanned_file
cursor.execute("""
    INSERT INTO comparison_matches (file_name_nist, sha256_nist, sha1_nist, md5_nist, file_name_local, sha256_local, sha1_local, md5_local)
    SELECT f.file_name AS file_name_nist,
           f.sha256 AS sha256_nist,
           f.sha1 AS sha1_nist,
           f.md5 AS md5_nist,
           s.file_name AS file_name_local,
           s.sha256 AS sha256_local,
           s.sha1 AS sha1_local,
           s.md5 AS md5_local
    FROM FILE f
    JOIN scanned_file s ON (f.sha256 = s.sha256 OR f.sha1 = s.sha1 OR f.md5 = s.md5)
""")

# Commit changes and close connection to the database
conn.commit()
conn.close()
