# Web版ビデオ通話対応 tasks.mdの作成

## 何を

`.kiro/specs/web-video-call-support/tasks.md`を新規作成。[design.md](../.kiro/specs/web-video-call-support/design.md)の設計（`external_api.js`の動的読み込み、`Meeting.web.tsx`実装、`readyToClose`とルーティングの連携、破棄処理、ローディング/エラー表示）を実行可能なタスクに分解し、あわせて`docs/frontend.md`・`manuals/video-call-testing.md`への追記、`npm run web`での動作確認（単独・2者間）をタスク化した。

## なぜ

ユーザーからの依頼。design.mdの内容に合意した後、実装（コード修正）に進む前段としてタスクリスト化した。
