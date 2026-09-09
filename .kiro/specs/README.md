# Specs（仕様駆動開発）

新機能に着手する際は、実装より先にここへ仕様を書く。1機能につき `.kiro/specs/<feature-slug>/` ディレクトリを作成し、以下の順に作成・レビューを進める。

1. `requirements.md` — 何を実現するか（What）。書き方は [docs/requirements-best-practices.md](../../docs/requirements-best-practices.md) を参照。
2. `design.md` — どう実装するか（How）。書き方は [docs/design-doc-best-practices.md](../../docs/design-doc-best-practices.md) を参照。
3. `tasks.md` — `design.md` を実行可能な単位に分解したタスクリスト。

## 進め方

- 各ドキュメントは前段階の内容に合意してから次に進む（requirements.md確定 → design.md着手 → design.md確定 → tasks.md着手）。要件・設計が固まっていない段階で実装を始めない。
- `<feature-slug>` は機能内容が分かるkebab-case（例: `community-management`）。
- 既存の規約（[.kiro/steering/](../steering/)、[docs/backend.md](../../docs/backend.md)、[docs/frontend.md](../../docs/frontend.md)）から意図的に外れる設計をする場合は、design.md内にその理由を明記する。
