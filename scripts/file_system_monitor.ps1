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
    event_type TEXT,
    sha256 VARCHAR,
    sha1 VARCHAR,
    md5 VARCHAR,
    tlsh VARCHAR
)"
$command.ExecuteNonQuery()

$connection.Close()

# make FileSystemWatcher
$fsw = New-Object IO.FileSystemWatcher $folder -Property @{
    IncludeSubdirectories = $true               
    NotifyFilter = [IO.NotifyFilters]'FileName, LastWrite, DirectoryName'
}

#when a file event occurs from the file event manager
#Create, Delete, Change, Rename
$action = {
    param($sender, $eventArgs)

    $directoryPath = [System.IO.Path]::GetDirectoryName($eventArgs.FullPath)
    $fileName = [System.IO.Path]::GetFileName($eventArgs.FullPath)
    $extension = [System.IO.Path]::GetExtension($eventArgs.FullPath)

    if ($extension -in $monitoredExtensions) {
        
        # Generate file hashes
        $sha256Hash = (Get-FileHash -Path $eventArgs.FullPath -Algorithm SHA256).Hash
        $sha1Hash = (Get-FileHash -Path $eventArgs.FullPath -Algorithm SHA1).Hash
        $md5Hash = (Get-FileHash -Path $eventArgs.FullPath -Algorithm MD5).Hash
        $tlshHash = python .\generate_tlsh.py $eventArgs.FullPath

        $connection = New-Object -TypeName System.Data.SQLite.SQLiteConnection -ArgumentList ("Data Source=$dbPath")
        $connection.Open()

        $command = $connection.CreateCommand()
        $command.CommandText = "INSERT INTO file_monitor_events (file_name, path, file_extension, date_time, event_type, sha256, sha1, md5, tlsh) VALUES (@Name, @Path, @Extension, @Time, @Type, @Sha256, @Sha1, @Md5, @Tlsh)"

        $command.Parameters.AddWithValue("@Name", $fileName) | Out-Null
        $command.Parameters.AddWithValue("@Path", $directoryPath) | Out-Null
        $command.Parameters.AddWithValue("@Extension", $extension) | Out-Null
        $command.Parameters.AddWithValue("@Time", $(Get-Date -Format u)) | Out-Null
        $command.Parameters.AddWithValue("@Type", $eventArgs.ChangeType) | Out-Null
        $command.Parameters.AddWithValue("@Sha256", $sha256Hash) | Out-Null
        $command.Parameters.AddWithValue("@Sha1", $sha1Hash) | Out-Null
        $command.Parameters.AddWithValue("@Md5", $md5Hash) | Out-Null
        $command.Parameters.AddWithValue("@Tlsh", $tlshHash) | Out-Null

        try {
            $command.ExecuteNonQuery() | Out-Null
        } catch {
            Write-Output "$(Get-Date): Failed to insert event into database. Error: $($_.Exception.Message)"
        }

        $connection.Close()
    }
}

Register-ObjectEvent $fsw Created -SourceIdentifier FileCreated -Action $action
Register-ObjectEvent $fsw Deleted -SourceIdentifier FileDeleted -Action $action
Register-ObjectEvent $fsw Changed -SourceIdentifier FileChanged -Action $action
Register-ObjectEvent $fsw Renamed -SourceIdentifier FileRenamed -Action $action

# keep running
Wait-Event