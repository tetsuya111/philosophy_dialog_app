# 作業ログ: 実機インストール失敗（INSTALL_FAILED_USER_RESTRICTED）の要件定義作成

## 何を行ったか

- `.kiro/specs/fix-adb-install-user-restricted/requirements.md`を新規作成した。
- `adb shell getprop`で端末情報を確認し、Xiaomi Redmi Note 9S（Android 12、MIUI）と特定した。

## なぜ行ったか

[.kiro/specs/fix-jitsi-config-network-error/](../.kiro/specs/fix-jitsi-config-network-error/)の切り分け（Jitsi接続の不安定さがエミュレータ固有の問題かを実機で確認する）のため、ユーザーの実機に`npm run android:win`でdev clientをインストールしようとしたところ、`INSTALL_FAILED_USER_RESTRICTED: Install canceled by user`で失敗した。

端末がXiaomi（MIUI）と判明したため、MIUI固有の既知の制限（通常の「USBデバッグ」とは別に「USBデバッグ（セキュリティ設定）」を有効にしないとADB経由のアプリインストールがブロックされる）が原因である可能性が高いと判断し、その対応手順をrequirements.mdにまとめた。本件はJitsi接続調査本体とは独立した、実機テストの前提条件（インストール障害）の解消が目的のため、別specとして切り出した。
