Unregister-Event -SourceIdentifier FileCreated -ErrorAction SilentlyContinue
Unregister-Event -SourceIdentifier FileDeleted -ErrorAction SilentlyContinue
Unregister-Event -SourceIdentifier FileChanged -ErrorAction SilentlyContinue
Unregister-Event -SourceIdentifier FileRenamed -ErrorAction SilentlyContinue

$configPath = Join-Path -Path $PSScriptRoot -ChildPath '..\user_config.json'
$config = Get-Content -Raw -Path $configPath | ConvertFrom-Json
$dbPath = Join-Path -Path $config.database.path -ChildPath $config.database.filename

#monitoring
$folder = $config.scanning.root_dir
$monitoredExtensions = $config.file_monitoring.file_types

# SQLite .NET library
$dllPath = Join-Path -Path $PSScriptRoot -ChildPath '..\System.Data.SQLite.dll'
Add-Type -Path $dllPath

$connection = New-Object -TypeName System.Data.SQLite.SQLiteConnection -ArgumentList ("Data Source=$dbPath")
$connection.Open()

$command = $connection.CreateCommand()
$command.CommandText = "
CREATE TABLE IF NOT EXISTS file_monitor_events (
    file_name VARCHAR,
    path VARCHAR,
    file_extension VARCHAR,
    date_time TIMESTAMP,
    event_type TEXT
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

    $directoryPath = [System.IO.Path]::GetDirectoryName($eventArgs.FullPath)
    $fileName = [System.IO.Path]::GetFileName($eventArgs.FullPath)
    $extension = [System.IO.Path]::GetExtension($eventArgs.FullPath)

    if ($extension -in $monitoredExtensions) {
        $connection = New-Object -TypeName System.Data.SQLite.SQLiteConnection -ArgumentList ("Data Source=$dbPath")
        $connection.Open()

        $command = $connection.CreateCommand()
        $command.CommandText = "INSERT INTO file_monitor_events (file_name, path, file_extension, date_time, event_type) VALUES (@Name, @Path, @Extension, @Time, @Type)"

        $command.Parameters.AddWithValue("@Name", $fileName) | Out-Null
        $command.Parameters.AddWithValue("@Path", $directoryPath) | Out-Null
        $command.Parameters.AddWithValue("@Extension", $extension) | Out-Null
        $command.Parameters.AddWithValue("@Time", $(Get-Date -Format u)) | Out-Null
        $command.Parameters.AddWithValue("@Type", $eventArgs.ChangeType) | Out-Null

        try {
            $command.ExecuteNonQuery() | Out-Null
        } catch {
            Write-Output "$(Get-Date): Failed to insert event into database. Error: $($_.Exception.Message)"
        }

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