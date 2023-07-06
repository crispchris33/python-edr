from flask import Flask, render_template, request, jsonify
import sqlite3
import json
import os

app = Flask(__name__)

# Loading DB info
with open('user_config.json') as f:
    data = json.load(f)
    db_path = data['database']['path']
    db_file = data['database']['filename']
    db_full_path = os.path.join(db_path, db_file)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/actions')
def actions():
    return render_template('actions.html')

@app.route('/monitoring')
def monitoring():
    return render_template('monitoring.html')

@app.route('/data', methods=['POST'])
def data():
    draw = request.form.get('draw')
    start = request.form.get('start', type=int)
    length = request.form.get('length', type=int)
    
    con = sqlite3.connect(db_full_path)
    con.row_factory = sqlite3.Row  # column access by name
    cur = con.cursor()

    cur.execute("SELECT * FROM tlsh_scanner LIMIT ? OFFSET ?", (length, start))
    rows = cur.fetchall()

    # converts rows to dictionaries
    data = [dict(row) for row in rows]

    cur.execute("SELECT COUNT(*) FROM tlsh_scanner")
    total_records = cur.fetchone()[0]

    return jsonify({
        "draw": draw,
        "recordsTotal": total_records,
        "recordsFiltered": total_records,
        "data": data
    })

if __name__ == "__main__":
    app.run(debug=True)
