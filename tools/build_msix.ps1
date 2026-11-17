$makeappx = "C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x64\makeappx.exe"
$signtool = "C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x64\signtool.exe"

$shellDir = Join-Path $PSScriptRoot "modern_shell"
$msixPath = Join-Path $PSScriptRoot "zipper9_shell.msix"
$pfxPath = Join-Path $PSScriptRoot "zipper9_cert.pfx"
$pfxPass = "zipper9pass"

# 0. dllhost 종료 및 기존 패키지 언인스톨
Stop-Process -Name dllhost -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 500

Write-Host "0. Removing old package if exists..."
$oldPkg = Get-AppxPackage *zipper9* -ErrorAction SilentlyContinue
if ($oldPkg) {
    Remove-AppxPackage -Package $oldPkg.PackageFullName -ErrorAction SilentlyContinue
    Write-Host "Removed: $($oldPkg.PackageFullName)"
}

# 1. 내부 바이너리 직접 디지털 서명
Write-Host "1. Signing inner binaries (zipper9_shell.dll, tiny.exe)..."
& $signtool sign /fd SHA256 /f $pfxPath /p $pfxPass "$shellDir\zipper9_shell.dll"
& $signtool sign /fd SHA256 /f $pfxPath /p $pfxPass "$shellDir\tiny.exe"

# 2. 패키지 파일 빌드
if (Test-Path $msixPath) {
    Remove-Item -Force $msixPath
}

Write-Host "2. Building MSIX package with makeappx..."
& $makeappx pack /d $shellDir /p $msixPath /o /nv
if ($LASTEXITCODE -ne 0) {
    Write-Error "makeappx failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}

# 3. MSIX 패키지 자체 서명
Write-Host "3. Signing MSIX package with signtool..."
& $signtool sign /fd SHA256 /f $pfxPath /p $pfxPass $msixPath
if ($LASTEXITCODE -ne 0) {
    Write-Error "signtool failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}

# 4. Windows에 등록
Write-Host "4. Registering MSIX package to Windows..."
Add-AppxPackage -Path $msixPath

Write-Host "5. Verifying package registration..."
Get-AppxPackage *zipper9* | Format-Table Name, PackageFullName, Version, Status, InstallLocation
