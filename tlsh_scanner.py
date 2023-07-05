import os
import sqlite3
from datetime import datetime
import tlsh
import json

# Load user configuration
with open('user_config.json') as json_file:
    config = json.load(json_file)

# Get config variables
db_path = config['database']['path']
db_filename = config['database']['filename']
root_dir = config['scanning']['root_dir']
file_types = tuple(config['scanning']['file_types'])  # convert to tuple for 'endswith'

# Function to generate tlsh hash of a file
def generate_tlsh_hash(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        tlsh_hash = tlsh.hash(data)
    return tlsh_hash

# Get current date and time
date_time = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
file_date_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def main():

    print("Running the main script...")

    # Connect to SQLite database (it will be created if it doesn't exist)
    conn = sqlite3.connect(db_path + db_filename)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tlsh_scanner (
            tlsh VARCHAR,
            file_name VARCHAR,
            file_size INTEGER,
            date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Initialize the exception list
    exceptions = []

    # Initialize a counter for new records
    new_records = 0

    for foldername, subfolders, filenames in os.walk(root_dir):
        for filename in filenames:
            # Check file extension
            if not filename.endswith(file_types):
                continue

            try:
                # Generate full path to file
                file_path = os.path.join(foldername, filename)

                # Generate tlsh hash
                tlsh_hash = generate_tlsh_hash(file_path)

                # Get file size
                file_size = os.path.getsize(file_path)

                # Check if the file already exists
                cursor.execute("""
                    SELECT * FROM tlsh_scanner 
                    WHERE tlsh = ? AND file_name = ? AND file_size = ?
                """, (tlsh_hash, file_path, file_size))

                # If the record exists, skip to the next file
                if cursor.fetchone() is not None:
                    exceptions.append(f"Duplicate record found for file {file_path}. Skipping.")
                    continue

                # Insert data into the database
                cursor.execute("""
                    INSERT INTO tlsh_scanner(tlsh, file_name, file_size)
                    VALUES (?, ?, ?)
                """, (tlsh_hash, file_path, file_size))

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

    # Commit changes and close connection to the database
    conn.commit()
    conn.close()

    # Print the number of new records added
    print(f"Added {new_records} new records.")

    # Create a HTML file and write exceptions into it
    try:
        with open(f"exception_list_{file_date_time}.html", "w") as f:
            f.write("<html>\n<body>\n<table>\n")
            for i, exception in enumerate(exceptions, start=1):
                f.write(f"<tr><td>{i}</td><td>{exception}</td></tr>\n")
            f.write("</table>\n</body>\n</html>")
    except Exception as e:
        print(f"Failed to write to HTML file due to: {e}")

main()
