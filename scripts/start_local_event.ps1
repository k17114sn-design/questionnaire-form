<#
  イベント当日、会場のWi-Fiでアプリを配信するための起動スクリプト。
  同一ネットワーク内の端末（子供のスマホ・タブレット）からアクセスできるよう 0.0.0.0 でバインドする。

  事前に一度だけ、管理者権限のPowerShellで以下を実行してファイアウォールを開けておくこと：
    New-NetFirewallRule -DisplayName "GX Hero App" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
#>

param(
  [int]$Port = 8000
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

# 管理画面パスワード・セッション鍵：環境変数が無ければ当日限りのランダム値を生成して表示する
if (-not $env:ADMIN_PASSWORD) {
    $env:ADMIN_PASSWORD = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 10 | ForEach-Object { [char]$_ })
}
if (-not $env:SECRET_KEY) {
    $env:SECRET_KEY = [guid]::NewGuid().ToString("N") + [guid]::NewGuid().ToString("N")
}

Write-Host "=================================================="
Write-Host " GXヒーロー診断 - 会場Wi-Fi版 起動"
Write-Host "=================================================="
Write-Host "管理画面パスワード: $($env:ADMIN_PASSWORD)"
Write-Host ""
Write-Host "参加者に案内するURL候補（会場Wi-FiのIPアドレス）:"
Get-NetIPAddress -AddressFamily IPv4 |
    Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.254.*" } |
    ForEach-Object { Write-Host "  http://$($_.IPAddress):$Port" }
Write-Host ""
Write-Host "上記アドレスのうち、会場Wi-Fiのアダプタに対応するものを選び、"
Write-Host "管理画面のQRコード発行機能でQR化して掲示してください。"
Write-Host "=================================================="

$fwRule = Get-NetFirewallRule -DisplayName "GX Hero App" -ErrorAction SilentlyContinue
if (-not $fwRule) {
    Write-Warning "ファイアウォール許可ルール「GX Hero App」が見つかりません。"
    Write-Warning "管理者権限のPowerShellで以下を一度だけ実行してから再度起動してください："
    Write-Warning ('  New-NetFirewallRule -DisplayName ' + [char]34 + 'GX Hero App' + [char]34 + " -Direction Inbound -Protocol TCP -LocalPort $Port -Action Allow")
}

& "$root\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port $Port
