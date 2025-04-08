$ApiUrl = "https://api.github.com/repos/mozilla/sccache/releases/latest"
# Relative to Engine/Scripts/Programmer
$Root = $PSScriptRoot
$SccacheDir = "$Root/../../Binaries/ThirdParty/Sccache"

# Remove existing sccache exe if it exists
if (Test-Path "$SccacheDir/sccache.exe") { Remove-Item -Force "$SccacheDir/sccache.exe" }

try {
	$Response = Invoke-WebRequest -Uri $ApiUrl -ErrorAction Stop
} catch {
	Write-Error "uh oh!"
	return
}

$ApiJson = $Response.Content | ConvertFrom-Json
$Tag = $ApiJson.tag_name
if ([string]::IsNullOrEmpty($Tag)) {
	Write-Error "Failed to get Sccahe tag_name from $ApiUrl!"
	return
}

$FileName = "sccache-$Tag-x86_64-pc-windows-msvc.zip"
foreach($Asset in $ApiJson.assets) {
    if ($Asset.name -eq $FileName)
    {
        $FoundAssetUrl = $Asset.browser_download_url
        break
    }
}

if ([string]::IsNullOrEmpty($FoundAssetUrl))
{
    Write-Error "Failed to get asset url for $FileName!"
	return
}

# Check if folder exiss, if not create it
If(!(Test-Path -PathType Container $SccacheDir))
{
    # Create it silently
    New-Item -Path $SccacheDir -ItemType Directory | Out-Null
}

# Sccache include a subfolder inside the zip, yay
$FolderName = "sccache-$Tag-x86_64-pc-windows-msvc" 

# Download and unzip file
Invoke-WebRequest -Uri $FoundAssetUrl -OutFile "$SccacheDir/$FileName"
Expand-Archive -Path "$SccacheDir/$FileName" -DestinationPath "$SccacheDir"

# Move sccache.exe to correct location
Move-Item -Path "$SccacheDir/$FolderName/sccache.exe" -Destination "$SccacheDir"

# Clear files
Remove-Item -Path "$SccacheDir/$FileName"
Remove-Item -Path "$SccacheDir/$FolderName" -Recurse -Force -EA Continue 

Write-Host $FoundAssetUrl