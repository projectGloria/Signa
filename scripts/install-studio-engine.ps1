# One-time provisioning for running Signa Studio from source on Windows x64.
$ErrorActionPreference = 'Stop'
$studio = Join-Path $env:LOCALAPPDATA 'SignaStudio'
$models = Join-Path $studio 'models'
New-Item -ItemType Directory -Force $models | Out-Null

function Install-VerifiedFile($uri, $destination, $sha256) {
    if ((Test-Path -LiteralPath $destination) -and
        (Get-FileHash -LiteralPath $destination).Hash -eq $sha256) { return }
    $tempFile = "$destination.$([guid]::NewGuid()).part"
    try {
        & curl.exe --fail --location --retry 2 -o $tempFile $uri
        if ($LASTEXITCODE -ne 0) { throw "Download failed for $destination" }
        if ((Get-FileHash -LiteralPath $tempFile).Hash -ne $sha256) {
            throw "Checksum mismatch for $destination"
        }
        Move-Item -LiteralPath $tempFile -Destination $destination -Force
    } finally {
        if (Test-Path -LiteralPath $tempFile) { Remove-Item -LiteralPath $tempFile }
    }
}

$release = 'https://github.com/leejet/stable-diffusion.cpp/releases/download/master-1106-532d2c1'
$archive = Join-Path $studio 'engine.zip'
Install-VerifiedFile "$release/sd-master-532d2c1-bin-win-vulkan-x64.zip" $archive '3E66222C87CA27074E1FD8CE79706EEF17A8AAF39949906AA1BEE7E060F22ECC'
Expand-Archive -LiteralPath $archive -DestinationPath (Join-Path $studio 'engine') -Force
$revision = 'https://huggingface.co/Comfy-Org/stable-diffusion-v1-5-archive/resolve/9cfd069101959ca3828bf9c04a4419870832b74f'
Install-VerifiedFile "$revision/v1-5-pruned-emaonly-fp16.safetensors" (Join-Path $models 'sd15.safetensors') 'E9476A13728CD75D8279F6EC8BAD753A66A1957CA375A1464DC63B37DB6E3916'
Install-VerifiedFile 'https://raw.githubusercontent.com/CompVis/stable-diffusion/main/LICENSE' (Join-Path $models 'LICENSE.txt') 'BE351EBE7AC01BCDBB018639AADCFD38F136B7DC3F2A3D4D3A24DB51D1B210EF'
Write-Output "Offline generation files are ready in $studio"
