import os
import sqlite3
from datetime import datetime
import tlsh
import json

# Load config
with open('user_config.json') as json_file:
    config = json.load(json_file)

db_path = config['database']['path']
db_filename = config['database']['filename']
root_dir = config['scanning']['root_dir']
file_types = tuple(config['scanning']['file_types']) 

# Function to generate tlsh
def generate_tlsh_hash(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        tlsh_hash = tlsh.hash(data)
    return tlsh_hash

date_time = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
file_date_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def main():

    print("Running the main script...")

    conn = sqlite3.connect(db_path + db_filename)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tlsh_scanner (
            tlsh VARCHAR,
            file_name VARCHAR,
            path VARCHAR,
            file_size INTEGER,
            date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    exceptions = []
    new_records = 0

    for foldername, subfolders, filenames in os.walk(root_dir):
        for filename in filenames:
            if not filename.endswith(file_types):
                continue

            try:
                file_path = os.path.join(foldername, filename)
                directory_path, file_name = os.path.split(file_path)
                tlsh_hash = generate_tlsh_hash(file_path)
                file_size = os.path.getsize(file_path)

                # Check if the file already exists
                cursor.execute("""
                    SELECT * FROM tlsh_scanner 
                    WHERE tlsh = ? AND file_name = ? AND path = ? AND file_size = ?
                """, (tlsh_hash, file_name, directory_path, file_size))

                if cursor.fetchone() is not None:
                    exceptions.append(f"Duplicate record found for file {file_path}. Skipping.")
                    continue

                # Insert data into db
                cursor.execute("""
                    INSERT INTO tlsh_scanner(tlsh, file_name, path, file_size)
                    VALUES (?, ?, ?, ?)
                """, (tlsh_hash, file_name, directory_path, file_size))

                new_records += 1

            # Exceptions
            except PermissionError as e:
                exceptions.append(f"Permission denied for file {file_path}. Error message: {e}. Skipping.")

            except sqlite3.IntegrityError as e:
                exceptions.append(f"Duplicate hash {tlsh_hash} for file {file_path}. Skipping due to: {e}")

            except Exception as e:
                exception_message = f"Failed to process file {file_path} due to {e}"
                print(exception_message)
                exceptions.append(exception_message)

    conn.commit()
    conn.close()

    print(f"Added {new_records} new records.")

    # Create exceptions file
    try:
        with open(f"exception_list_{file_date_time}.html", "w") as f:
            f.write("<html>\n<body>\n<table>\n")
            for i, exception in enumerate(exceptions, start=1):
                f.write(f"<tr><td>{i}</td><td>{exception}</td></tr>\n")
            f.write("</table>\n</body>\n</html>")
    except Exception as e:
        print(f"Failed to write to HTML file due to: {e}")

main()
