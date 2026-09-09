# ビデオ通話基盤の自前ホスティング化: requirements.md新規作成

## 何を

`.kiro/specs/self-host-jitsi-server/requirements.md` を新規作成した。現状`meet.jit.si`（公開サーバー）に依存しているビデオ通話基盤（`frontend/components/Meeting.tsx`・`Meeting.web.tsx`）を自前ホスティングのJitsi Meetに切り替える構想について、要件・懸念点・サーバー構築方式の選択肢を整理した。

## なぜ

ユーザーから「自前ホスティングに修正したい。懸念点・批判点を重点的に、サーバー構築方法も検討して」という依頼があったため。移行の技術要件だけでなく、運用体制がゼロであること・コスト・TURN/NAT越え・セキュリティ・バージョン互換性・優先度の妥当性といった批判的観点を明記し、即移行を推奨するのではなく判断材料の整理を主目的とした。構築方式は単一VPS+公式docker-compose構成（案A）を暫定の有力案としつつ、最終決定はdesign.mdに委ねる形にした。
