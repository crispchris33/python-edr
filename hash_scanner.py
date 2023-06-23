import os
import hashlib
import sqlite3
from datetime import datetime

#from permissions import check_permissions_and_run

# Function to generate sha256, sha1, and md5 hash of a file
def generate_hashes(file_path):
    sha256_hash = hashlib.sha256()
    sha1_hash = hashlib.sha1()
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
            sha1_hash.update(byte_block)
            md5_hash.update(byte_block)
    return sha256_hash.hexdigest(), sha1_hash.hexdigest(), md5_hash.hexdigest()

# Get current date and time
date_time = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
file_date_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def main():

    print("Running the main script...")

    # Connect to SQLite database (it will be created if it doesn't exist)
    conn = sqlite3.connect('D:\Hashing DB\RDS_2023.06.1_modern_minimal.db')
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scanned_file (
            sha256 VARCHAR,
            sha1 VARCHAR,
            md5 VARCHAR,
            file_name VARCHAR,
            file_size INTEGER,
            date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Initialize the exception list
    exceptions = []

    root_dir = 'C:/'  # root directory to start from
    for foldername, subfolders, filenames in os.walk(root_dir):
        for filename in filenames:
            # Check file extension
            if not (filename.endswith('.exe') or filename.endswith('.dll')):
                continue

            try:
                # Generate full path to file
                file_path = os.path.join(foldername, filename)

                # Generate hashes
                sha256_hash, sha1_hash, md5_hash = generate_hashes(file_path)

                # Get file size
                file_size = os.path.getsize(file_path)

                # Check if the file already exists
                cursor.execute("""
                    SELECT * FROM scanned_file 
                    WHERE sha256 = ? AND sha1 = ? AND md5 = ? AND file_name = ? AND file_size = ?
                """, (sha256_hash, sha1_hash, md5_hash, file_path, file_size))

                # If the record exists, skip to the next file
                if cursor.fetchone() is not None:
                    exceptions.append(f"Duplicate record found for file {file_path}. Skipping.")
                    continue

                # Insert data into the database
                cursor.execute("""
                    INSERT INTO scanned_file(sha256, sha1, md5, file_name, file_size)
                    VALUES (?, ?, ?, ?, ?)
                """, (sha256_hash, sha1_hash, md5_hash, file_path, file_size))


            # Exceptions
            except PermissionError as e:
                exceptions.append(f"Permission denied for file {file_path}. Error message: {e}. Skipping.")

            except sqlite3.IntegrityError as e:
                exceptions.append(f"Duplicate hash {sha256_hash} for file {file_path}. Skipping due to: {e}")

            except Exception as e:
                exception_message = f"Failed to process file {file_path} due to {e}"
                print(exception_message)
                exceptions.append(exception_message)

    # Commit changes and close connection to the database
    conn.commit()
    conn.close()

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