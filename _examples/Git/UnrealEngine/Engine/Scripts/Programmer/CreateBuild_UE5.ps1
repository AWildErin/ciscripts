$Root = $PSScriptRoot
$GLabDir = "$Root/../../Binaries/ThirdParty/glab"

$Repo = "[REDACTED]"
$EnvVars = "MANUAL_PIPELINE:InstalledBuild,RELEASE_VERSION:v1.5.0"
$Branch = "5.3/dev"

$GLabExec = Start-Process -FilePath "$GLabDir/glab.exe" -ArgumentList "ci run -b $Branch --variables-env $EnvVars -R $repo" -NoNewWindow -PassThru -Wait -ErrorAction Stop

if ($GLabExec.ExitCode -ne 0) {
	Write-Error "Failed to build sccache! Please check output!"
	return
}

