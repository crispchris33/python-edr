Unregister-Event -SourceIdentifier FileCreated -ErrorAction SilentlyContinue
Unregister-Event -SourceIdentifier FileDeleted -ErrorAction SilentlyContinue
Unregister-Event -SourceIdentifier FileChanged -ErrorAction SilentlyContinue
Unregister-Event -SourceIdentifier FileRenamed -ErrorAction SilentlyContinue

$config = Get-Content -Raw -Path '.\user_config.json' | ConvertFrom-Json
$dbPath = Join-Path -Path $config.database.path -ChildPath $config.database.filename

#monitoring
$folder = $config.scanning.root_dir
$monitoredExtensions = $config.file_monitoring.file_types

# SQLite .NET library
Add-Type -Path '.\System.Data.SQLite.dll'

$connection = New-Object -TypeName System.Data.SQLite.SQLiteConnection -ArgumentList ("Data Source=$dbPath")
$connection.Open()

$command = $connection.CreateCommand()
$command.CommandText = "
CREATE TABLE IF NOT EXISTS file_monitor_events (
    FileName VARCHAR,
    FilePath VARCHAR,
    FileExtension VARCHAR,
    EventTime TIMESTAMP,
    EventType TEXT
)"
$command.ExecuteNonQuery()

$connection.Close()

# make FileSystemWatcher
$fsw = New-Object IO.FileSystemWatcher $folder -Property @{
    IncludeSubdirectories = $true               
    NotifyFilter = [IO.NotifyFilters]'FileName, LastWrite, DirectoryName'
}

#when a file event occurs
$action = {
    param($sender, $eventArgs)
    
    $extension = [System.IO.Path]::GetExtension($eventArgs.FullPath)

    if ($extension -in $monitoredExtensions) {
        $connection = New-Object -TypeName System.Data.SQLite.SQLiteConnection -ArgumentList ("Data Source=$dbPath")
        $connection.Open()

        $command = $connection.CreateCommand()
        $command.CommandText = "INSERT INTO file_monitor_events (FileName, FilePath, FileExtension, EventTime, EventType) VALUES (@Name, @Path, @Extension, @Time, @Type)"

        $command.Parameters.AddWithValue("@Name", $eventArgs.Name) | Out-Null
        $command.Parameters.AddWithValue("@Path", $eventArgs.FullPath) | Out-Null
        $command.Parameters.AddWithValue("@Extension", $extension) | Out-Null
        $command.Parameters.AddWithValue("@Time", $(Get-Date -Format u)) | Out-Null
        $command.Parameters.AddWithValue("@Type", $eventArgs.ChangeType) | Out-Null

        $command.ExecuteNonQuery()
        $connection.Close()

        # TODO: Add hashing function here later
    }
}

Register-ObjectEvent $fsw Created -SourceIdentifier FileCreated -Action $action
Register-ObjectEvent $fsw Deleted -SourceIdentifier FileDeleted -Action $action
Register-ObjectEvent $fsw Changed -SourceIdentifier FileChanged -Action $action
Register-ObjectEvent $fsw Renamed -SourceIdentifier FileRenamed -Action $action

# keep running
Wait-Event