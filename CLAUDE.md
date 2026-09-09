 CLAUDE.md

このファイルは、このリポジトリで作業する Claude Code (claude.ai/code) 向けのガイドです。

**このファイルおよび今後の追記・更新はすべて日本語で記述すること。**

## プロジェクト構成

このリポジトリは以下の2つの独立したアプリからなるモノレポです。

- `backend/` — Django REST Framework による API（`djangorestframework-simplejwt` を使った JWT 認証）
- `frontend/` — Expo（React Native, TypeScript, expo-router）によるモバイル/Webフロントエンド

両者は共通のビルドツールを持たず、それぞれ独立して開発・起動します。フロントエンドはバックエンドとHTTP経由でのみやり取りします。

## ドキュメント一覧

詳細は各ドキュメントに一本化しており、このファイルはそこへの索引を兼ねる。新しい詳細情報を追記する際は、このファイルに直接書かず該当ドキュメントを更新すること。

- [docs/backend.md](docs/backend.md) — バックエンドのセットアップ、コマンド、設定、アーキテクチャ
- [docs/frontend.md](docs/frontend.md) — フロントエンドのセットアップ、コマンド、設定、アーキテクチャ
- [docs/prompt-guidelines.md](docs/prompt-guidelines.md) — プロンプト・Markdownファイル作成の指針
- [docs/requirements-best-practices.md](docs/requirements-best-practices.md) — 要件定義（[.kiro/specs/](.kiro/specs/README.md)のrequirements.md）を書く際のベストプラクティス
- [docs/design-doc-best-practices.md](docs/design-doc-best-practices.md) — 設計ドキュメント（[.kiro/specs/](.kiro/specs/README.md)のdesign.md）を書く際のベストプラクティス

## マニュアル（`manuals/`）

機能のテスト手順・操作手順など、実行手順そのものを説明するドキュメントは `manuals/` 配下に作成する（`docs/`はセットアップ・アーキテクチャ等の説明、`.kiro/specs/`は仕様策定のためのドキュメントであり、動作確認・操作の手順書はこれらと区別して `manuals/` に置く）。新しいマニュアルを作成した際は、以下に一覧を追記すること。

- [manuals/video-call-testing.md](manuals/video-call-testing.md) — ビデオ通話（Jitsi Meet SDK）のテスト手順

## 開発ワークフロー（`.kiro/`）

AWS Kiroの Steering / Specs / Agent Hooks の考え方を、このリポジトリでは `.kiro/` 配下 + Claude Code本来のhooks機構で再現している。

- [.kiro/steering/](.kiro/steering/) — 常時参照される永続的なプロジェクトコンテキスト（product.md / tech.md / structure.md）。新しいセッションでもプロダクトの前提を把握できるようにする。
- [.kiro/specs/](.kiro/specs/README.md) — 機能ごとの requirements.md → design.md → tasks.md。新機能に着手する際は実装より先にここへ仕様を書く。
- [.kiro/hooks/](.kiro/hooks/README.md) — イベント駆動の自動化の一覧。実体は `.claude/settings.json` のhooks設定（例: frontendファイル編集後の自動lint修正）。

## 作業ログ

- 以下のいずれかを行った場合は、`logs/`以下に「何を・なぜ行ったか」を簡潔に記録すること。
  - 要件定義・設計ドキュメント（`.kiro/specs/` 配下の `requirements.md` / `design.md` / `tasks.md` など）の新規作成・修正
  - プロジェクトのコード・設定への修正（`backend/` / `frontend/` 配下のファイル変更全般）
- ログは修正内容ごとに1ファイルを作成する。1つのファイルに複数の修正内容を混在させないこと。
- ファイル名は `logs/<yyyymmdd_hhMMss>_<種別>_<内容がわかる名前>.md` とし、ファイル名だけで作成日時・修正の種類・内容が判別できるようにする（日時は作成時点のものを付与する。例: 仕様関連なら `20260906_143000_spec_community-management-requirements.md`、CLAUDE.md自体の修正なら `20260906_143000_claude-md_token-saving-practices.md` など）。
- ログファイルは必ずMarkdown形式（`.md`）で作成する。
- 日々の作業内容を後から追跡できるようにするための記録であり、コミットメッセージやPR説明の代わりにはしない（両方に残す）。

## トークン使用量の節約

Claude Codeとのやり取りではコンテキスト消費（トークン使用量）を最小限に抑えることを常に意識する。

- ファイルを読み込む際は必要最小限のファイル・範囲のみ読み込むこと（無関係なファイルは開かない、大きなファイルは該当箇所のみ`offset`/`limit`で読む）。
- 直前の操作結果や会話内で既に把握できている内容を、確認目的で再度読み込まないこと（例: Edit/Write直後に同じファイルを読み直さない）。
- コードベース全体を対象とした調査では、いきなり多数のファイルを開かず、Grep/Globで対象を絞り込んでから必要なファイルだけを読むこと。
- ビルドログ・テスト結果など出力が長大になりうるコマンドは、フィルタリングして必要な部分のみを確認すること。
- ファイルの一部を変更する場合はWriteによる全文書き換えではなく、Editによる差分編集を優先すること。
- 広範囲・多段階の調査はサブエージェントに委譲し、詳細な探索結果ではなく要約のみをメインの会話コンテキストに持ち込むこと。
- 同じ内容を複数のドキュメントに重複して書かない（[docs/prompt-guidelines.md](docs/prompt-guidelines.md)の単一情報源の原則に従う）。

## frontendの起動について

- `expo start` / `npx expo run:android` / `npm run android:win` など、frontendを起動・実行するコマンドをClaude Codeが自動でバックグラウンド実行しないこと。プロセスの状態を目視で追えず、完了通知も確実には機能しない（バックグラウンドタスクが完了扱いになった後もMetroプロセスが残り続けた事例がある）ため、状況を誤認しやすい。
- frontendの起動・実機/エミュレータでの動作確認が必要な場面では、Claude Codeが代わりに実行するのではなく、ユーザーに手動実行を促すこと。

## 横断的な注意点

- リポジトリ内の `README.md`（ルート、`backend/`、`frontend/` などすべて）は日本語で記載すること。
- バックエンドとフロントエンドはそれぞれ独立した `.gitignore` を持つ。環境依存の設定（`.env` など）を追加する際は両方を確認すること。
- バックエンドに新しいアプリを追加する際は `accounts/` の構成に倣い、`INSTALLED_APPS` への登録とURLの `include()` を忘れないこと（詳細は [docs/backend.md](docs/backend.md)）。
- バックエンドはCORS未対応（`django-cors-headers` 未導入）。フロントエンドからブラウザ経由（Expo Web等）でAPIを呼び出す機能を追加する場合は、CORS設定の追加が必要になる点に注意すること。