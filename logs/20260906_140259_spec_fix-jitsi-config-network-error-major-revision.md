# 作業ログ: Jitsi切断・再参加エラーのrequirements.md大幅改訂

## 何を行ったか

`.kiro/specs/fix-jitsi-config-network-error/requirements.md`を全面的に書き直した。

## なぜ行ったか

ユーザーから、実機とエミュレータの両方で共通して以下の流れが再現するとの報告があった。

1. 「一人で対話を開始する」を押す
2. 「ミーティングに参加しています」表示
3. 「あなたは切断されました」ダイアログ（キャンセル/今すぐ再参加）
4. 「今すぐ再参加」を押すと`invalid url`エラー

これまで「今すぐ参加する（Join Now）」という別のボタンの話だと誤解しており、要件定義もその誤解に基づいていた。今回の報告で「今すぐ再参加（Rejoin Now）」＝エミュレータで見た切断ダイアログと同一のものだと判明し、**実機でも同じ切断が再現する**ことが確定した。

これにより、旧版の要件定義に書いていた「Androidエミュレータの仮想ネットワーク（NAT）が原因」という結論は誤りだったと判断し撤回した。

`@jitsi/react-native-sdk`のソースコード（`react/features/base/dialog/components/native/PageReloadDialog.tsx`、`react/features/app/actions.native.ts`）を確認し、「今すぐ再参加」ボタンが`reloadNow()`→`appNavigate()`を呼び出し、redux stateの`locationURL`からURLを再構築して`new URL(...)`に渡す実装になっていることを特定した。この`new URL()`が不正な文字列を渡されると標準で`TypeError: Invalid URL`を投げるため、`invalid url`エラーの発生箇所として最も疑わしいと判断した。

原因（アプリ設定起因／共有ネットワーク環境起因／meet.jit.si公開サーバー起因）を切り分けるための具体的な調査項目（PCブラウザでの同一room再現確認、別回線での実機接続確認等）をオープンクエスチョンとして整理した。
