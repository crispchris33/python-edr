import os
import sqlite3
import json
import tlsh

dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
config_path = os.path.join(dir_path, 'user_config.json')

with open(config_path) as json_file:
    config = json.load(json_file)

db_full_path = config['database']['path'] + config['database']['filename']

def tlsh_compare(tlsh_hash1, tlsh_hash2):
    hash1 = tlsh.Tlsh()
    hash2 = tlsh.Tlsh()

    hash1.fromTlshStr(tlsh_hash1)
    hash2.fromTlshStr(tlsh_hash2)

    similarity_score = hash1.hash_diff(hash2)

    return similarity_score

def compare_tlsh(tlsh_hash):
    conn = sqlite3.connect(db_full_path)
    cur = conn.cursor()

    cur.execute("SELECT file_name, tlsh FROM tlsh_scanner")
    rows = cur.fetchall()

    comparison_data = []
    for row in rows:
        file_name, other_tlsh = row
        similarity_score = tlsh_compare(tlsh_hash, other_tlsh)

        if similarity_score > 0:
            comparison_data.append({
                'file_name': file_name,
                'tlsh': other_tlsh,
                'similarity_score': similarity_score
            })

    conn.close()
    return comparison_data
