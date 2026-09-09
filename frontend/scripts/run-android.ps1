# npx expo run:android の起動用スクリプト。
# このPCの環境では、AndroidエミュレータからMetro(8081)への接続が
# 10.0.2.2 経由だと(Norton等のHTTP検査が原因と見られる)chunked encoding
# エラーで失敗し、「Reloading」から進まなくなることが分かっている。
# adb reverseでlocalhost経由の接続に固定することで回避する。
#
# 使い方: frontend ディレクトリで `npm run android:win`、
#         または `powershell -ExecutionPolicy Bypass -File scripts\run-android.ps1` を実行する。

Set-Location (Join-Path $PSScriptRoot "..")

if ($env:ANDROID_HOME) {
    $adb = Join-Path $env:ANDROID_HOME "platform-tools\adb.exe"
} elseif ($env:ANDROID_SDK_ROOT) {
    $adb = Join-Path $env:ANDROID_SDK_ROOT "platform-tools\adb.exe"
} else {
    $adb = Join-Path $env:LOCALAPPDATA "Android\Sdk\platform-tools\adb.exe"
}
if (-not (Test-Path $adb)) { $adb = "adb" }

Write-Host "[run-android] デバイス/エミュレータの接続を待機します..."
& $adb wait-for-device

Write-Host "[run-android] adb reverse tcp:8081 -> tcp:8081 を設定します..."
& $adb reverse tcp:8081 tcp:8081

Write-Host "[run-android] ビルド完了後にlocalhost接続を強制する処理を裏で予約します..."
Start-Process powershell -ArgumentList @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-File", (Join-Path $PSScriptRoot "force-localhost-reconnect.ps1")
)

Write-Host "[run-android] npx expo run:android を起動します..."
npx expo run:android
