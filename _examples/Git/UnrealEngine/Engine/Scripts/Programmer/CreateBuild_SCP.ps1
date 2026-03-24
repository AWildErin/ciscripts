$Root = $PSScriptRoot
$GLabDir = "$Root/../../Binaries/ThirdParty/glab"

$Repo = "[REDACTED]"
$EnvVars = "MANUAL_PIPELINE:Release,STEAM_BRANCH:internal"
$Branch = "main"

$GLabExec = Start-Process -FilePath "$GLabDir/glab.exe" -ArgumentList "ci run -b $Branch --variables-env $EnvVars -R $repo" -NoNewWindow -PassThru -Wait -ErrorAction Stop

if ($GLabExec.ExitCode -ne 0) {
	Write-Error "Failed to build sccache! Please check output!"
	return
}

