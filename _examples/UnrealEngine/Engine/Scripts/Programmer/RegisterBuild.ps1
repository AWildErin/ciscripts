## AWE_FILE_BEGIN - Erin
# Registers the current Unreal install to AWE_Custom used by our Projects

$Root = $PSScriptRoot

$UEDir = "$Root/../../../"
$AbsUEDir = Resolve-Path $UEDir
# Replace slashes
$AbsUEDir = $AbsUEDir -replace '\\', '/'
# Remove trailing slash
$AbsUEDir = $AbsUEDir -replace '/$', ''

$RegPath = "HKCU:\SOFTWARE\Epic Games\Unreal Engine\Builds"
$RegKey = "AWE_Custom"

Write-Host "Registering $RegKey Build to $AbsUEDir"

Set-ItemProperty -Path $RegPath -Name $RegKey -Value $AbsUEDir -Type String -Force
