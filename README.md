# philosophy_dialog_app

ランダムマッチ哲学対話アプリ。ユーザーを4人単位でランダムにマッチングし、Jitsi Meetによるグループビデオ通話上で哲学対話を行う。

## 構成

モノレポで、以下の2つの独立したアプリからなる。両者はHTTP経由でのみやり取りする。

- [backend/](backend/README.md) — Django REST Framework によるAPI（JWT認証、ランダムマッチング）
- [frontend/](frontend/README.md) — Expo（React Native, TypeScript）によるモバイル/Webフロントエンド

## ドキュメント

- [CLAUDE.md](CLAUDE.md) — Claude Code向けの開発ガイド（ドキュメント一覧の索引も兼ねる）
- [docs/](docs/) — バックエンド/フロントエンドのセットアップ・アーキテクチャや、ドキュメント作成のベストプラクティス
- [.kiro/](.kiro/) — プロダクト概要・技術スタック・仕様（requirements/design/tasks）
