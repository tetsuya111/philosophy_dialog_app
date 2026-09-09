# run-android.ps1 から裏で呼ばれるヘルパー。
# Metroのビルド・アプリの起動を少し待ってから、adb reverse を再設定し、
# dev clientに明示的に localhost:8081 へ接続させる。
# （10.0.2.2経由だとNorton等のHTTP検査でchunked encodingが壊れて
#   接続できない環境があるため、adb reverse経由のlocalhostに固定する）

if ($env:ANDROID_HOME) {
    $adb = Join-Path $env:ANDROID_HOME "platform-tools\adb.exe"
} elseif ($env:ANDROID_SDK_ROOT) {
    $adb = Join-Path $env:ANDROID_SDK_ROOT "platform-tools\adb.exe"
} else {
    $adb = Join-Path $env:LOCALAPPDATA "Android\Sdk\platform-tools\adb.exe"
}
if (-not (Test-Path $adb)) { $adb = "adb" }

Write-Host "[force-localhost-reconnect] $(Get-Date) : ビルド・インストール完了を待機します (45秒)..."
Start-Sleep -Seconds 45

Write-Host "[force-localhost-reconnect] adb reverse tcp:8081 -> tcp:8081 を設定します..."
& $adb wait-for-device
& $adb reverse tcp:8081 tcp:8081

Write-Host "[force-localhost-reconnect] dev clientに localhost:8081 への接続を強制します..."
& $adb shell am start -a android.intent.action.VIEW -d "frontend://expo-development-client/?url=http%3A%2F%2Flocalhost%3A8081"

Write-Host "[force-localhost-reconnect] 完了しました。このウィンドウは閉じて構いません。"
Start-Sleep -Seconds 5
