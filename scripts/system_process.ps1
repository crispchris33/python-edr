#get data

$servicesData = Get-Service | ForEach-Object {
    $status = $_.Status
    $name = $_.Name
    $startType = (Get-WmiObject -Class Win32_Service -Filter "Name='$name'").StartMode
    $path = (Get-WmiObject -Class Win32_Service -Filter "Name='$name'").PathName
    New-Object PSObject -Property @{
        Name = $name
        Status = $status
        StartType = $startType
        Path = $path
    }
}

$totalServices = $servicesData.Count
$runningServices = ($servicesData | Where-Object {$_.Status -eq "Running"}).Count
$stoppedServices = ($servicesData | Where-Object {$_.Status -eq "Stopped"}).Count

#generate report

$htmlContent = "
<html>
<head>
<link rel='stylesheet' href='https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css'>
<style>
.table {
    table-layout: fixed;
    width: 1150px;
}
.table td, .table th {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.table td:nth-child(1), .table th:nth-child(1), 
.table td:nth-child(3), .table th:nth-child(3), 
.table td:nth-child(4), .table th:nth-child(4),
.table td:nth-child(5), .table th:nth-child(5) {
    width: 150px;
}
.table td:nth-child(2), .table th:nth-child(2),
.table td:nth-child(6), .table th:nth-child(6) {
    width: 350px;
}
</style>
</head>
<body>
<h1>System Processes Report</h1>
<p>Total number of services: $totalServices</p>
<p>Total number of running services: $runningServices</p>
<p>Total number of stopped services: $stoppedServices</p>
<table class='table'>
<thead>
<tr>
<th scope='col'>#</th>
<th scope='col'>Service Name</th>
<th scope='col'>Status</th>
<th scope='col'>Start Type</th>
<th scope='col'>Service Path</th>
</tr>
</thead>
<tbody>
"

for ($i=0; $i -lt $servicesData.Count; $i++) {
    $htmlContent += "
    <tr>
    <th scope='row'>$($i + 1)</th>
    <td>$($servicesData[$i].Name)</td>
    <td>$($servicesData[$i].Status)</td>
    <td>$($servicesData[$i].StartType)</td>
    <td><a href='$($servicesData[$i].Path)'>Open Path</a></td>
    </tr>
    "
}

$htmlContent += "
</tbody>
</table>
</body>
</html>
"

$outputDirectory = "./Reports/Services"

if (-not (Test-Path -Path $outputDirectory)) {
    New-Item -ItemType Directory -Force -Path $outputDirectory
}

$htmlFileName = "$outputDirectory/system_processes_$(Get-Date -Format 'yyyyMMdd_HHmmss').html"
$htmlContent | Out-File -FilePath $htmlFileName
$htmlFileName
