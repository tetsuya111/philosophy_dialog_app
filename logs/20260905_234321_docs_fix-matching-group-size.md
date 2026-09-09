# マッチング仕様の誤り修正（1対1 → 4人グループ）

## 何を

`.kiro/steering/product.md` と `docs/backend.md` の記述を、「1対1マッチング」から「`matching/signals.py`の`WAITING_LIMIT_N`（4）に基づく4人単位のグループマッチング」に修正。あわせて、現状フロントエンドの通話画面（`Home.tsx`）がバックエンドの`Room`と連携しておらず、手入力のルーム名でJitsi Meetに参加している点も明記した。

## なぜ

要件定義書をリバースエンジニアリングする過程で `matching/signals.py` を読み、直前に作成した `product.md`/`docs/backend.md` の「1対1マッチング」という記述が実装と異なる誤りだと判明したため。
