import os
import json
import requests
import sqlite3
from datetime import datetime

dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
config_path = os.path.join(dir_path, 'user_config.json')

with open(config_path) as json_file:
    config = json.load(json_file)

db_path = config['database']['path'] + config['database']['filename']
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("""
    CREATE TABLE IF NOT EXISTS virus_total_results (
        hash TEXT PRIMARY KEY,
        scan_date TEXT,
        positives INTEGER,
        permalink TEXT,
        scan_result TEXT,
        scan_id TEXT,
        sha1 TEXT,
        sha256 TEXT,
        md5 TEXT,
        resource TEXT,
        response_code INTEGER
    )
""")

#api
def vt_api_call(hash_type, hash_value):
    url = 'https://www.virustotal.com/api/v3/files/' + hash_value
    headers = {
        'x-apikey': config['virustotal_api_key']
    }
    response = requests.get(url, headers=headers)
    return response.json()

#insert data
def run_vt_check(hash_type, hash_value):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    response = vt_api_call(hash_type, hash_value)
    
    if 'data' in response:

        scan_date = response['data']['attributes']['last_analysis_date']
        positives = response['data']['attributes']['last_analysis_stats'].get('malicious', 0)
        total = response['data']['attributes']['last_analysis_stats'].get('total', 0)
        permalink = response['data']['attributes'].get('permalink', "Not Available")
        scan_result = response['data']['attributes'].get('scan_result', "Not Available")
        scan_id = response['data'].get('id', "Not Available")
        sha1 = response['data']['attributes'].get('sha1', "Not Available")
        sha256 = response['data']['attributes'].get('sha256', "Not Available")
        md5 = response['data']['attributes'].get('md5', "Not Available")
        resource = response['data'].get('resource', "Not Available")
        response_code = response['data'].get('response_code', "Not Available")

        c.execute("""
                INSERT INTO virus_total_results (hash, scan_date, positives, permalink, scan_result, scan_id, sha1, sha256, md5, resource, response_code)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (hash_value, scan_date, positives, permalink, scan_result, scan_id, sha1, sha256, md5, resource, response_code))

    else:
        print(f"No 'data' field in the response: {response}")
        c.execute("""
            INSERT INTO virus_total_results (hash, scan_date, positives, permalink, scan_result, scan_id, sha1, sha256, md5, resource, response_code)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (hash_value, datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), -1, "Not Available", "Not Available", "Not Available", "Not Available", "Not Available", "Not Available", "Not Available", -1))

    conn.commit()
    conn.close()
