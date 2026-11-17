# 1. 기존 구버전 인증서 정리
Get-ChildItem Cert:\CurrentUser\My | Where-Object { $_.Subject -like '*zipper9*' } | Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem Cert:\CurrentUser\TrustedPeople | Where-Object { $_.Subject -like '*zipper9*' } | Remove-Item -Force -ErrorAction SilentlyContinue

# 2. 코드 서명(Code Signing EKU 1.3.6.1.5.5.7.3.3)이 포함된 자체 서명 인증서 생성
$cert = New-SelfSignedCertificate -Type Custom `
    -Subject "CN=zipper9" `
    -KeyUsage DigitalSignature `
    -FriendlyName "zipper9 Shell Extension" `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}")

Write-Host "Created certificate: $($cert.Thumbprint)"

# 3. TrustedPeople 저장소에 등록
$peopleStore = New-Object System.Security.Cryptography.X509Certificates.X509Store("TrustedPeople", "CurrentUser")
$peopleStore.Open([System.Security.Cryptography.X509Certificates.OpenFlags]::ReadWrite)
$peopleStore.Add($cert)
$peopleStore.Close()

# 4. PFX 및 CER 파일 내보내기
$pwd = ConvertTo-SecureString -String "zipper9pass" -Force -AsPlainText
$pfxPath = Join-Path $PSScriptRoot "zipper9_cert.pfx"
$cerPath = Join-Path $PSScriptRoot "zipper9_cert.cer"

Export-PfxCertificate -Cert $cert -FilePath $pfxPath -Password $pwd | Out-Null
Export-Certificate -Cert $cert -FilePath $cerPath | Out-Null

Write-Host "Exported PFX to: $pfxPath"
Write-Host "Exported CER to: $cerPath"

# 5. certutil로 조용히 TrustedPeople에 동기화
& certutil -user -addstore -f "TrustedPeople" $cerPath
