# 実装タスク: ランダムコール（random-call）

| 項目 | 内容 |
| --- | --- |
| 対応する要件 | [requirements.md](requirements.md) |
| 対応する設計 | [design.md](design.md) |
| 作成日 | 2026-09-19 |

[design.md](design.md) を実行可能な単位に分解したもの。上から順に実施する。各タスクの（）内は対応する requirements のストーリー番号。

## タスク一覧

### タスク1: バックエンドの依存関係と設定

- [x] 1.1 `backend/requirements.txt` に `django-cors-headers` を追加する
- [x] 1.2 `settings.py` に `corsheaders` を `INSTALLED_APPS` に、`CorsMiddleware` を `CommonMiddleware` より前に追加する。`CORS_ALLOWED_ORIGINS` は環境変数（既定 `http://localhost:8081`）から読み、`CORS_ALLOW_HEADERS = (*default_headers, "x-client-id")` とする（6-6）
- [x] 1.3 `REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]` に `"matching_client": "30/hour"` を追加する
- [x] 1.4 `python manage.py check` が通ることを確認する

### タスク2: データモデルとマイグレーション

- [x] 2.1 `matching/constants.py` を作成する（`GROUP_SIZE` / `QUEUE_TIMEOUT` = 5分 / `ROOM_TTL` = 30分 / `ROOM_NAME_PREFIX`）（5-1）
- [x] 2.2 `matching/models.py` を design.md の「データモデル」どおりに変更する（`GuestClient` 追加、`WaitingQueue.user` を OneToOne 化、`Room` に `room_name` / `status` / `end_reason` / `expires_at` / `ended_at` を追加、`Room.users` を削除して `RoomMember` を追加、制約 `one_active_room_per_user`）（3-6）
- [x] 2.3 `matching` のマイグレーションを作成する。既存の `WaitingQueue` 行・`Room` 行を削除する `RunPython` を先頭に入れる
- [x] 2.4 `accounts.CustomUser.matching_status` と `accounts/choices.py` の `UserMatchingStatus` を削除し、`accounts/views.py` の `UserView` のレスポンスから `matching_status` を外す。`accounts` のマイグレーションを作成する
- [x] 2.5 `matching/signals.py` を削除し、`matching/apps.py` の `ready()` からシグナルの読み込みを外す
- [x] 2.6 `matching/admin.py` に新しいモデルを登録する（確認用）
- [x] 2.7 `python manage.py migrate` が通ることを確認する

### タスク3: 利用者識別子と認証クラス

- [x] 3.1 `matching/authentication.py` に `ClientIdAuthentication` を実装する（`X-Client-Id` を SHA-256 でハッシュ化して `GuestClient` を引く。`authenticate_header()` で 401 を返す）（6-2、1-3）
- [x] 3.2 `services.issue_client()` を実装する（ゲスト用 `CustomUser` を `set_unusable_password()` で作成、`GuestClient` にハッシュを保存、平文を返す）（6-1）

### タスク4: サービス層（待機列・グループ化）

- [x] 4.1 `services.get_state()` を実装する（design.md の「ユーザーの状態の導出」の表どおり）
- [x] 4.2 `join_queue()` / `try_form_group()` を実装する（1-2、1-4、1-5、3-1〜3-5、3-7）
- [x] 4.3 `cancel_queue()` を実装する。自分の元の待機行を必ず削除する（2-2〜2-4）
- [x] 4.4 `expire_stale()` の待機列タイムアウト部分を実装する。対象がなければ書き込まない（2-5、2-7）

### タスク5: サービス層（入退室・グループ終了・満了）

- [x] 5.1 `enter_call()` を実装する（`joined_at` は初回のみ。満了済みならその場で終了させて `RoomEnded`）（4-4〜4-6、4-8、5-5）
- [x] 5.2 `leave_call()` / `end_room()` を実装する（退室で `is_active=False`、全員退室で `ALL_LEFT`）（5-2〜5-4、5-8）
- [x] 5.3 `expire_stale()` の満了部分を実装する（5-5、5-6、5-9）
- [x] 5.4 サービス層に主要イベントのログ出力を追加する（design.md の「オブザーバビリティ」。利用者識別子・ルーム名は出さない）

### タスク6: API（ビュー・URL）

- [x] 6.1 `matching/serializers.py` に状態レスポンス（`status` / `server_time` / `waiting` / `room`）のシリアライザを実装する
- [x] 6.2 `matching/views.py` を作り直す。`client/`（認証不要・`ScopedRateThrottle`）、`status/`、`join/`、`cancel/`、`call/enter/`、`call/leave/`。発行以外は `ClientIdAuthentication` + `IsAuthenticated`。`status/`・`join/`・`call/enter/` の先頭で `expire_stale()` を呼ぶ。例外をエラー表どおりのステータス（409 / 404 / 410）に変換し、`OperationalError` は 503 にする
- [x] 6.3 `matching/urls.py` を更新する（既存の `GET join/`・`GET cancel/` は削除）

### タスク7: 管理コマンド

- [x] 7.1 `matching/management/commands/expire_random_calls.py` を実装する（`expire_stale()` を1回実行し、処理件数を出力する）
- [x] 7.2 `matching/management/commands/add_dummy_waiters.py` を実装する（`DEBUG=True` のときだけ、指定人数のダミーゲストを待機列に追加し `try_form_group()` を呼ぶ。手動確認用）

### タスク8: バックエンドのテスト

- [x] 8.1 `matching/tests.py` にサービス層のテストを書く（design.md の「テスト戦略」の項目。時刻は `timezone.now` を差し替えず、`created_at` / `expires_at` を過去に更新して再現した）
- [x] 8.2 API のテストを書く（ステータスコード、401、他人の状態が返らないこと、`GET` で状態が変わらないこと、レート制限）
- [x] 8.3 `python manage.py test` が全件通ることを確認する（既存の `accounts` のテストを含む）

### タスク9: フロントエンドの API クライアント

- [x] 9.1 `frontend/.env` に `EXPO_PUBLIC_API_BASE_URL=http://localhost:8000` を追加する（6-5）
- [x] 9.2 `lib/client-id.ts` を実装する（AsyncStorage のキー `randomCall.clientId`。なければ `POST client/` で発行して保存）（6-1、6-3）
- [x] 9.3 `lib/api-client.ts` を実装する（ベース URL と `X-Client-Id` の付与、401 のとき発行し直して1回だけ再試行）
- [x] 9.4 `lib/random-call.ts` に API 関数とレスポンスの型を実装する

### タスク10: Home画面とフック

- [x] 10.1 `hooks/use-random-call.ts` を実装する（`useFocusEffect` での状態取得、3秒ポーリング、`waiting → none` によるタイムアウト検知、`server_time` による時刻補正、1秒ごとの残り時間更新）（2-6、2-8、3-8、4-7、4-8）
- [x] 10.2 `app/(tabs)/index.tsx` の「対話をはじめる」を `Pressable` にし、状態に応じてボタン部分を切り替える（`none`: 対話をはじめる / `waiting`: 残り時間と「待機をやめる」 / `matched`・`in_call`: 残り時間と「対話に参加」）。通信エラー・タイムアウトの表示を追加する。レイアウトと「一人で対話を開始する」は変えない（1-1、1-6〜1-8、2-1、2-6、4-1）
- [x] 10.3 「対話に参加」で `enterCall()` → `router.push('/meeting', { room, mode: 'random', endsAt })` を実装する（4-2）

### タスク11: 通話画面

- [x] 11.1 `app/meeting.tsx` で `mode` / `endsAt` を受け取り、`mode === 'random'` のときだけ `onClose`（`leaveCall()`）と `endsAt` を `Meeting` に渡す（5-2）
- [x] 11.2 `components/Meeting.tsx` に任意の props `onClose` / `endsAt` を追加する（`onReadyToClose` で `onClose` を呼ぶ、`endsAt` で `close()`、`closedRef` で二重実行を防ぐ）（4-3、5-7）
- [x] 11.3 `components/Meeting.web.tsx` に同じ props を追加する（`readyToClose` で `onClose`、`endsAt` で `dispose()`）（4-3、5-7）
- [x] 11.4 `npm run lint` が通ることを確認する（変更・追加したファイルはエラーなし。既存の未使用テンプレート `components/hello-wave.tsx` / `parallax-scroll-view.tsx` / `hooks/use-color-scheme.web.ts` の3件は本スペック以前からのエラーで対象外）

### タスク12: ドキュメント・マニュアル

- [x] 12.1 [docs/backend.md](../../../docs/backend.md) を更新する（`matching` のモデル・API・利用者識別子による認証・管理コマンド、CORS 設定、`django-cors-headers` の追加）
- [x] 12.2 [docs/frontend.md](../../../docs/frontend.md) を更新する（`EXPO_PUBLIC_API_BASE_URL`、`lib/` の役割、Android で `adb reverse tcp:8000 tcp:8000` が必要なこと）
- [x] 12.3 [CLAUDE.md](../../../CLAUDE.md) の「横断的な注意点」の「バックエンドはCORS未対応」を現状に合わせて直す
- [x] 12.4 [.kiro/steering/](../../steering/) の product.md（主要フロー）・tech.md・structure.md を現状に合わせて更新する
- [x] 12.5 `manuals/random-call-testing.md` を作成し、CLAUDE.md のマニュアル一覧に追記する（4つの利用者識別子の用意の仕方、`add_dummy_waiters` の使い方、design.md の「テスト戦略」の確認項目）

### タスク13: 動作確認（ユーザーが手動で実施）

frontend の起動はユーザーが手動で行う（CLAUDE.md）。

- [ ] 13.1 Web 版（`npm run web`）で、待機・残り時間・取りやめ・タイムアウト表示を確認する
- [ ] 13.2 `add_dummy_waiters 3` と Web 版1台で、マッチングから入室・途中退室・再参加を確認する
- [ ] 13.3 Web 版と Android 版を混ぜた実際の複数クライアントで、同じルームに入り映像・音声が相互に届くことを確認する
- [ ] 13.4 Home への復帰・アプリ再起動後の再入室、満了による通話画面の自動終了を確認する（確認時は `ROOM_TTL` を一時的に短くしてよい）
- [ ] 13.5 「一人で対話を開始する」が今までどおり動くことを確認する

## Definition of Done

- requirements.md の全受け入れ基準が、バックエンドのテストまたは手動確認のいずれかで確認されている
- `python manage.py test` と `npm run lint` が通る
- タスク12のドキュメントが更新されている
- `logs/` に作業ログが記録されている（修正内容ごとに1ファイル）

## 実装順序・マイルストーン

1. **M1 バックエンド完成**（タスク1〜8）: API とテストだけで、待機・マッチング・入退室・満了が確認できる状態
2. **M2 フロントエンド接続**（タスク9〜11）: Web 版で一通り動く状態
3. **M3 仕上げ**（タスク12〜13）: ドキュメントの更新と、Android を含む手動確認
