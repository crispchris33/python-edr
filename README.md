# hash-script



# File System Watcher

Dependencies:

This project requires the System.Data.SQLite.dll library for SQLite support in .NET. This is not included in the GitHub repository. https://system.data.sqlite.org/


File System Watcher configuration step by step

1. Create basic scheduled task
2. Select: 
    -"Run whether user is logged on or not"
    -"Run with highest privileges"
3. Triggers: "At system startup"
4. Start a program: "powershell.exe"
5. Enter the argument and select the script in the root/scripts/:
    - ' -ExecutionPolicy Bypass -File "/directory/xyz.ps1" '
6. Start in: root/scripts/

Scheduled Task Command:
-ExecutionPolicy Bypass -File ""

