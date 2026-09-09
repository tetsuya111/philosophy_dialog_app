# Androidエミュレータの接続不良に対する恒久回避策の追加

## 何を

- `frontend/scripts/run-android.bat` / `frontend/scripts/force-localhost-reconnect.bat` を新規作成。`npx expo run:android`の代わりに使うと、`adb reverse tcp:8081 tcp:8081`を設定した上で、dev clientに`http://localhost:8081`への接続を明示的に強制する（ビルド完了を待って裏で自動実行）。
- `frontend/package.json`に`android:win`スクリプトを追加（`npm run android:win`で起動可能）。
- `manuals/video-call-testing.md`のトラブルシューティングに、この問題の原因と対処法を追記。

## なぜ

このプロジェクトの開発機（Windows + ノートン360）で、Androidエミュレータのdev clientが「Reloading...」から進まない不具合を調査した結果、エミュレータが既定で使う`10.0.2.2:8081`経由の接続で、生のTCP接続・pingは通るにもかかわらずHTTPレスポンス（chunked encoding）が壊れて失敗する事象を確認した（`java.net.ProtocolException: Expected leading [0-9a-fA-F] character but was 0xd`）。ファイアウォールでの単純な遮断ではなく、セキュリティソフトのWeb保護機能によるHTTP通信の検査・書き換えが原因と推測される。`adb reverse`経由の`localhost:8081`接続では問題なく繋がることを確認済みのため、これを毎回手動で行わずに済むようバッチスクリプト化した。
