$ErrorActionPreference = "Stop"

if ($env:OS -ne "Windows_NT" -or $env:PROCESSOR_ARCHITECTURE -ne "AMD64") {
    throw "The Windows builder requires Windows x86-64."
}

$AppDir = Split-Path -Parent $PSScriptRoot
$BuildDir = Join-Path $AppDir "build\windows"
$DistDir = Join-Path $AppDir "dist"
$Uv = $env:LOCAL_AI_APP_UV
if (-not $Uv) {
    $UvCommand = Get-Command uv -ErrorAction SilentlyContinue
    if ($UvCommand) { $Uv = $UvCommand.Source }
}
if (-not $Uv) { throw "uv is required to build the package." }

Remove-Item -LiteralPath $BuildDir -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $BuildDir, $DistDir | Out-Null
& $Uv run --no-project --python 3.12 python (Join-Path $AppDir "packaging\create_payload.py") `
    --output (Join-Path $BuildDir "payload.zip")
if ($LASTEXITCODE) { exit $LASTEXITCODE }

$PyInstallerArgs = @(
    "run", "--no-project", "--python", "3.12", "--with", "pyinstaller==6.19.0",
    "pyinstaller", "--clean", "--noconfirm", "--onefile",
    "--name", "local-reader-no-gpu",
    "--distpath", (Join-Path $BuildDir "pyinstaller-dist"),
    "--workpath", (Join-Path $BuildDir "pyinstaller-work"),
    "--specpath", $BuildDir,
    "--add-data", "$(Join-Path $BuildDir 'payload.zip');.",
    (Join-Path $AppDir "packaging\launcher.py")
)
& $Uv @PyInstallerArgs
if ($LASTEXITCODE) { exit $LASTEXITCODE }

$Output = Join-Path $DistDir "Local-Reader-No-GPU-0.3.2-windows-x86_64.exe"
Copy-Item (Join-Path $BuildDir "pyinstaller-dist\local-reader-no-gpu.exe") $Output -Force
Write-Host "Built $Output"
