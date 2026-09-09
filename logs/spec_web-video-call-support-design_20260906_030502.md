# Web版ビデオ通話対応 requirements.mdの確定・design.mdの作成

## 何を

ユーザーが`.kiro/specs/web-video-call-support/requirements.md`のオープンクエスチョン3件（Web埋め込み方式はJitsi Meet API(`external_api.js`)を採用、DOM要素の扱いは設計に一任、Web版に実際の通話機能を持たせるという解釈は合意済み）に回答したのを受け、requirements.mdから該当セクションを削除し決定事項をスコープに反映。あわせて`.kiro/specs/web-video-call-support/design.md`を新規作成し、`external_api.js`を`react-native-web`の`View`のDOMノードに埋め込む設計（案A採用、単純iframeのみ案・react-native-webview案は却下として記録）を記載した。

## なぜ

ユーザーからの依頼。要件確認が完了したため設計フェーズに進んだ。新規ネイティブ依存を追加しない方針([requirements.md](../.kiro/specs/web-video-call-support/requirements.md)の非機能要件)に沿って、`react-native-webview`等を使わずスクリプト動的読み込み＋View参照で実現する設計とした。
