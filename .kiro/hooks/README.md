# Agent Hooks（イベント駆動の自動化）

このリポジトリでは、AWS Kiro の Agent Hooks に相当する仕組みを Claude Code 本来の hooks 機構（`.claude/settings.json` の `hooks` 設定）で実現する。イベント（ファイル編集後など）をトリガーに、決まったコマンドを自動実行したい場合はここに追記し、実体は `.claude/settings.json` に設定する。

## 現在の設定

現時点では `.claude/settings.json` は未作成で、hooksは未設定。

## 追加する場合

- 新しいhookを追加した際は、この一覧にも「何のイベントで・何を実行するか」を追記する（実体は `.claude/settings.json` のみに書き、内容をここに重複して書かない）。
- hookの書式・利用可能なイベントはClaude Code本体のドキュメントを参照する。
