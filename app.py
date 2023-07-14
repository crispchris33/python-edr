from flask import Flask, render_template, request, jsonify
import sqlite3
import json
import os
import urllib.parse
from urllib.parse import unquote
from scripts.virus_check import run_vt_check

app = Flask(__name__)

with open('user_config.json') as json_file:
    config = json.load(json_file)

# Loading DB info
with open('user_config.json') as f:
    data = json.load(f)
    db_path = data['database']['path']
    db_file = data['database']['filename']
    db_full_path = os.path.join(db_path, db_file)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/single_item')
def single_item():
    file_name = request.args.get('file')
    print(f"File name: {file_name}")
    return render_template('single_item.html', file_name=file_name)

@app.route('/actions')
def actions():
    return render_template('actions.html')

@app.route('/monitoring')
def monitoring():
    return render_template('monitoring.html')

#index.html
@app.route('/data', methods=['POST'])
def data():
    draw = request.form.get('draw')
    start = request.form.get('start', type=int)
    length = request.form.get('length', type=int)
    search_value = request.form.get('search[value]', default="")
    columns = ["file_name", "file_size", "date_time"]
    order_column = request.form.get('order[0][column]', type=int, default=0)
    order_column = min(order_column, len(columns) - 1)
    order_direction = request.form.get('order[0][dir]', default="asc")
    order_column_name = columns[order_column]
    
    con = sqlite3.connect(db_full_path)
    con.row_factory = sqlite3.Row  # column access by name
    cur = con.cursor()

    cur.execute(f"""
        SELECT * 
        FROM tlsh_scanner
        WHERE file_name LIKE ? OR file_size LIKE ? OR date_time LIKE ?
        ORDER BY {order_column_name} {order_direction}
        LIMIT ? OFFSET ?
    """, (f"%{search_value}%", f"%{search_value}%", f"%{search_value}%", length, start))
    rows = cur.fetchall()

    data = [dict(row) for row in rows]

    cur.execute("SELECT COUNT(*) FROM tlsh_scanner")
    total_records = cur.fetchone()[0]

    return jsonify({
        "draw": draw,
        "recordsTotal": total_records,
        "recordsFiltered": total_records,
        "data": data
    })

@app.route('/data_scanned_file', methods=['POST'])
def data_scanned_file():
    file_name = request.form.get('file')
    draw = request.form.get('draw')
    start = request.form.get('start', type=int)
    length = request.form.get('length', type=int)

    con = sqlite3.connect(db_full_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute("SELECT * FROM scanned_file WHERE file_name = ? LIMIT ? OFFSET ?", (file_name, length, start))
    rows = cur.fetchall()

    data = [dict(row) for row in rows]

    cur.execute("SELECT COUNT(*) FROM scanned_file WHERE file_name = ?", (file_name,))
    total_records = cur.fetchone()[0]

    return jsonify({
        "draw": draw,
        "recordsTotal": total_records,
        "recordsFiltered": total_records,
        "data": data
    })

@app.route('/data_tlsh_scanner', methods=['POST'])
def data_tlsh_scanner():
    file_name = request.form.get('file')
    draw = request.form.get('draw')
    start = request.form.get('start', type=int)
    length = request.form.get('length', type=int)

    con = sqlite3.connect(db_full_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute("SELECT * FROM tlsh_scanner WHERE file_name = ? LIMIT ? OFFSET ?", (file_name, length, start))
    rows = cur.fetchall()

    data = [dict(row) for row in rows]

    cur.execute("SELECT COUNT(*) FROM tlsh_scanner WHERE file_name = ?", (file_name,))
    total_records = cur.fetchone()[0]

    return jsonify({
        "draw": draw,
        "recordsTotal": total_records,
        "recordsFiltered": total_records,
        "data": data
    })

#single_item template routes for populating hash display tables
@app.route('/data_sha256', methods=['POST'])
def data_sha256():
    raw_file_name = request.form.get('file')
    file_name = unquote(raw_file_name)
    draw = request.form.get('draw')
    start = request.form.get('start', type=int)
    length = request.form.get('length', type=int)
    search_value = request.form.get('search[value]', default="")
    columns = ["sha256", "path", "file_size", "date_time"]
    order_column = request.form.get('order[0][column]', type=int, default=0)
    order_column = min(order_column, len(columns) - 1)
    order_direction = request.form.get('order[0][dir]', default="asc")
    order_column_name = columns[order_column]

    con = sqlite3.connect(db_full_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute(f"""
        SELECT sha256, path, file_size, date_time
        FROM scanned_file
        WHERE file_name = ? AND (sha256 LIKE ? OR path LIKE ? OR file_size LIKE ? OR date_time LIKE ?)
        ORDER BY {order_column_name} {order_direction}
        LIMIT ? OFFSET ?
    """, (file_name, f"%{search_value}%", f"%{search_value}%", f"%{search_value}%", f"%{search_value}%", length, start))
    rows = cur.fetchall()

    data = [dict(row) for row in rows]

    cur.execute("SELECT COUNT(*) FROM scanned_file WHERE file_name = ?", (file_name,))
    total_records = cur.fetchone()[0]

    return jsonify({
        "draw": draw,
        "recordsTotal": total_records,
        "recordsFiltered": total_records,
        "data": data
    })

@app.route('/data_sha1', methods=['POST'])
def data_sha1():
    file_name = request.form.get('file')
    file_name = urllib.parse.unquote(file_name)
    file_name = file_name.replace('\\\\', '\\')
    app.logger.info('Received file_name: %s', file_name)
    draw = request.form.get('draw')
    start = request.form.get('start', type=int)
    length = request.form.get('length', type=int)

    con = sqlite3.connect(db_full_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute("SELECT sha1, path, file_size, date_time FROM scanned_file WHERE file_name = ? LIMIT ? OFFSET ?", (file_name, length, start))
    rows = cur.fetchall()

    data = [dict(row) for row in rows]

    cur.execute("SELECT COUNT(*) FROM scanned_file WHERE file_name = ?", (file_name,))
    total_records = cur.fetchone()[0]

    return jsonify({
        "draw": draw,
        "recordsTotal": total_records,
        "recordsFiltered": total_records,
        "data": data
    })

@app.route('/data_md5', methods=['POST'])
def data_md5():
    file_name = request.form.get('file')
    file_name = urllib.parse.unquote(file_name)
    file_name = file_name.replace('\\\\', '\\')
    app.logger.info('Received file_name: %s', file_name)
    draw = request.form.get('draw')
    start = request.form.get('start', type=int)
    length = request.form.get('length', type=int)

    con = sqlite3.connect(db_full_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute("SELECT md5, path, file_size, date_time FROM scanned_file WHERE file_name = ? LIMIT ? OFFSET ?", (file_name, length, start))
    rows = cur.fetchall()

    data = [dict(row) for row in rows]

    cur.execute("SELECT COUNT(*) FROM scanned_file WHERE file_name = ?", (file_name,))
    total_records = cur.fetchone()[0]

    return jsonify({
        "draw": draw,
        "recordsTotal": total_records,
        "recordsFiltered": total_records,
        "data": data
    })

@app.route('/data_tlsh', methods=['POST'])
def data_tlsh():
    file_name = request.form.get('file')
    file_name = urllib.parse.unquote(file_name)
    file_name = file_name.replace('\\\\', '\\')
    app.logger.info('Received file_name: %s', file_name)
    draw = request.form.get('draw')
    start = request.form.get('start', type=int)
    length = request.form.get('length', type=int)

    con = sqlite3.connect(db_full_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute("SELECT tlsh, path, file_size, date_time FROM tlsh_scanner WHERE file_name = ? LIMIT ? OFFSET ?", (file_name, length, start))
    rows = cur.fetchall()

    data = [dict(row) for row in rows]

    cur.execute("SELECT COUNT(*) FROM tlsh_scanner WHERE file_name = ?", (file_name,))
    total_records = cur.fetchone()[0]

    return jsonify({
        "draw": draw,
        "recordsTotal": total_records,
        "recordsFiltered": total_records,
        "data": data
    })

#single_item.html - retrieve hash check status
@app.route('/get_hash_status', methods=['POST'])
def get_hash_status():
    hash_value = request.json.get('hash_value')

    con = sqlite3.connect(db_full_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute("SELECT positives FROM virus_total_results WHERE hash = ? OR sha1 = ? OR sha256 = ? OR md5 = ?", 
                (hash_value, hash_value, hash_value, hash_value,))
    result = cur.fetchone()

    if result:
        positives = result[0]
        return jsonify({'positives': positives})
    else:
        return jsonify({'error': 'hash not found'}), 404

# VT Stuff

@app.route('/run_vt_check', methods=['POST'])
def handle_vt_check():
    try:

        data = request.get_json()
        hash_type = data['hash_type']
        hash_value = data['hash_value']

        run_vt_check(hash_type, hash_value)

        return jsonify({'message': 'Scan complete'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#hash_result.html

@app.route('/hash_result')
def hash_result():
    hash_value = request.args.get('hash')
    file_name = request.args.get('file_name')

    con = sqlite3.connect(db_full_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute("SELECT * FROM virus_total_results WHERE hash = ?", (hash_value,))
    result = cur.fetchone()

    if result:
        return render_template('hash_result.html', hash=hash_value, file_name=file_name, scan_date=result['scan_date'], positives=result['positives'], permalink=result['permalink'], scan_result=result['scan_result'], scan_id=result['scan_id'], sha1=result['sha1'], sha256=result['sha256'], md5=result['md5'], resource=result['resource'], response_code=result['response_code'])
    else:
        return render_template('hash_result.html', hash=hash_value, file_name=file_name)


if __name__ == "__main__":
    app.run(debug=True)
