# hash-script


# Set up 

Check Virtual Environment Dependencies
    -requirements.txt

Setup user_config.json
    -change name of "example_user_config.json" > "user_config.json"

Launch Flask in the Venv
Start Virtual Environment:
"source venv/bin/activate"

Start Flask:
"flask run"

Populate Database With Scripts:
-hash_scanner.py
-tlsh_scanner.py
-File System Monitor(below)

# File System Monitor

Dependencies:

This project requires the System.Data.SQLite.dll library for SQLite support in .NET. This is not included in the GitHub repository. https://system.data.sqlite.org/


File System Watcher scheduled task configuration step by step

1. Create basic scheduled task
2. Select: 
    -"Run whether user is logged on or not"
    -"Run with highest privileges"
3. Triggers: "At system startup"
4. Start a program: "powershell.exe"
5. Enter the argument and select the script in the root/scripts/:
    - ' -ExecutionPolicy Bypass -File "/directory/file_system_monitor.ps1" '
6. Start in: root/scripts/