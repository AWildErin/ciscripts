# AWE_FILE_BEGIN - Erin
# Builds a copy of sccache with the correct configration and places it inside "Engine/Binaries/Thirdpaty/Sccache/"
# It exists in here because I'm not sure if I will upstream our custom sccache changes.
#
# Requirements:
# - Rust. Sccache developers recommend getting it via RustUp (https://rustup.rs/)
# - Read the building guide: https://github.com/AWildErin/sccache/tree/awe-changes?tab=readme-ov-file#build-requirements
#
# Setup:
# 1. Clone https://github.com/awilderin/sccache and checkout "awe-changes"
# 	 (Example: git clone -b awe-changes https://github.com/awilderin/sccache)
# 2. Run this script
#	 (Example: ./Engine/Scripts/Programmer/BuildSccache.ps1 -RepoPath "Path/To/My/Repo" )
# 3. Remember to update which commit sccache was built from in Engine/Binaries/ThirdParty/Sccache/sccache.tps.

param (
	[string]$RepoPath,
	[string]$Version = ""
)

$Target = "x86_64-pc-windows-msvc"
$Root = $PSScriptRoot
$SccacheDir = "$Root/../../Binaries/ThirdParty/Sccache"

Write-Host "Building Sccache located at: $RepoPath"

if (![System.IO.File]::Exists("$RepoPath/Cargo.toml")) {
	Write-Error "Failed to find cargo.toml at $RepoPath!";
	return
}

Write-Host "Found Cargo.toml"

Write-Host "Building..."
$CargoBuild = Start-Process -WorkingDirectory $RepoPath -FilePath "cargo" -ArgumentList "build --locked --release --bin sccache --target $Target --features=openssl/vendored" -NoNewWindow -PassThru -Wait -ErrorAction Stop

if ($CargoBuild.ExitCode -ne 0) {
	Write-Error "Failed to build sccache! Please check output!"
	return
}

Write-Host "Compile successful"
if ([System.IO.File]::Exists("$RepoPath/target/$target/release/sccache.exe")) {
	Write-Host "Copying sccache.exe..."

	Copy-Item -Path "$RepoPath/target/$target/release/sccache.exe" -Destination "$SccacheDir/sccache.exe"
}

Write-Host "Finished!"