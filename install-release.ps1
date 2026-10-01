# Download a versioned native package, verify SHA-256, then launch it.
$ErrorActionPreference = "Stop"
$LasVersion = "0.3.4"
if ($env:OS -ne "Windows_NT" -or $env:PROCESSOR_ARCHITECTURE -ne "AMD64") {
    throw "Windows x86-64 is required."
}
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$LasAsset = "Local-Reader-No-GPU-$LasVersion-windows-x86_64.exe"
$LasBase = "https://github.com/davidealbertazzi97-jpg/LOCAL-READER-NO-GPU/releases/download/v$LasVersion"
$LasTemp = Join-Path ([IO.Path]::GetTempPath()) ("las-install-" + [guid]::NewGuid())
New-Item -ItemType Directory -Path $LasTemp | Out-Null
try {
    Write-Host "Scarico e verifico il pacchetto / Downloading and verifying the package..."
    Invoke-WebRequest -UseBasicParsing "$LasBase/SHA256SUMS.txt" -OutFile (Join-Path $LasTemp "SHA256SUMS.txt")
    Invoke-WebRequest -UseBasicParsing "$LasBase/$LasAsset" -OutFile (Join-Path $LasTemp $LasAsset)
    $LasPattern = '^([a-f0-9]{64})  ' + [regex]::Escape($LasAsset) + '$'
    $LasLines = @(Get-Content (Join-Path $LasTemp "SHA256SUMS.txt") | Where-Object { $_ -match $LasPattern })
    if ($LasLines.Count -ne 1) { throw "Missing or invalid checksum." }
    $LasExpected = $LasLines[0].Substring(0, 64)
    $LasActual = (Get-FileHash -Algorithm SHA256 (Join-Path $LasTemp $LasAsset)).Hash
    if ($LasActual -ne $LasExpected) { throw "Checksum mismatch. Nothing executed." }
    $LasDest = Join-Path $env:LOCALAPPDATA "Local Reader No GPU\packages\$LasVersion"
    New-Item -ItemType Directory -Force -Path $LasDest | Out-Null
    $LasExe = Join-Path $LasDest $LasAsset
    Copy-Item -LiteralPath (Join-Path $LasTemp $LasAsset) -Destination $LasExe -Force
    Start-Process -FilePath $LasExe -Wait
} finally {
    Remove-Item -LiteralPath $LasTemp -Recurse -Force
}
