# 技術設計: ランダムコール（random-call）

| 項目 | 内容 |
| --- | --- |
| ステータス | Draft |
| 作成者 | tetsuya111 |
| 作成日 | 2026-09-19 |
| 更新日 | 2026-09-19（実装時の差分を反映: ログは structlog、`.gitignore` の `lib/` 除外） |
| 対応する要件 | [requirements.md](requirements.md) |

## 概要 (TL;DR)

既存の `backend/matching/` を作り直し、「待機列 → 4人でグループ化 → グループ専用の Jitsi ルーム名を発行 → 入室・退室・30分で満了」までを1つのサービス層（`matching/services.py`）に集約する。ログインなしで使うため、サーバーが発行した利用者識別子（`X-Client-Id` ヘッダー）ごとにゲスト用の `CustomUser` を自動作成し、既存の `CustomUser` への外部キー構成を維持する。フロントエンドは Home画面の「対話をはじめる」ボタンに待機・マッチング状態のポーリング（3秒間隔）をつなぎ、既存の通話画面（`app/meeting.tsx` + `components/Meeting*.tsx`）にグループのルーム名を渡して入室させる。

## ゴール・Non-Goals

ゴールは [requirements.md](requirements.md) の「ゴール」と同じ。本設計で追加する技術的な Non-Goals は次の通り。

- 常駐ワーカー（Celery 等）・WebSocket（Django Channels 等）の導入。期限切れ処理と画面反映はポーリングと遅延評価で行う
- 本番向けの DB（PostgreSQL 等）への移行。開発環境の SQLite のまま動くことを前提とする（同時実行の扱いは「同時実行の考え方」参照）
- ゲスト用ユーザーの削除・棚卸し。不要になったゲストは残り続けるが、現時点の利用規模では問題にならない
- フロントエンドの自動テスト基盤の導入（現状 Jest 等が未導入のため、lint と手動確認で検証する）
- iOS 固有の対応

## 既存アーキテクチャとの整合性

| 項目 | 既存 | 本設計 | 判断 |
| --- | --- | --- | --- |
| 認証 | 全 API が `JWTAuthentication` + `IsAuthenticated`（`settings.py` の `REST_FRAMEWORK`） | `matching` の API のみ独自の `ClientIdAuthentication` に差し替える。グローバル設定と `accounts` は変更しない | 意図的な逸脱。要件（ログインなし）のため。ビュー単位の `authentication_classes` 指定で影響範囲を `matching` に閉じる |
| ユーザーの状態 | `CustomUser.matching_status`（`NONE` / `WATING` / `JOINED`） | フィールドを廃止し、待機列・グループのメンバー行の有無から導出する | 既存の「成立時に `NONE` に戻る」不整合の根本対策（「検討した代替案」参照） |
| グループ化 | `WaitingQueue` の `post_save` シグナル（`matching/signals.py`） | サービス関数 `join_queue()` から明示的に呼ぶ。`signals.py` は削除 | 既知の課題（排他なし）の修正 |
| join / cancel | `GET` | `POST` | 既知の課題の修正。現状フロントエンドから呼ばれていないため互換性の考慮は不要 |
| 新規アプリ | — | 追加しない（既存の `matching` を拡張） | [docs/backend.md](../../../docs/backend.md) の規約どおり。`INSTALLED_APPS` / `include()` は登録済み |
| CORS | 未導入 | `django-cors-headers` を導入 | Web 版（Expo Web）から API を呼ぶため（CLAUDE.md の注意点どおり） |
| フロントエンドの API 呼び出し | 仕組みなし | `frontend/lib/` を新設し、API クライアントを置く | [docs/frontend.md](../../../docs/frontend.md) の「設定」節の方針（`EXPO_PUBLIC_` プレフィックスの環境変数）に従う |

## アーキテクチャ概要

```
[Home画面 app/(tabs)/index.tsx]
   │ useRandomCall()（hooks/use-random-call.ts）
   │   ├ フォーカス中かつ status≠none の間、3秒ごとに GET /status/
   │   └ join / cancel / enter を呼ぶ
   │
   │ lib/random-call.ts ── lib/api-client.ts（X-Client-Id 付与、EXPO_PUBLIC_API_BASE_URL）
   │                             └ lib/client-id.ts（AsyncStorage に利用者識別子を保存）
   ▼
[Django /api/matching/*]
   views.py（ClientIdAuthentication）→ services.py（transaction.atomic + select_for_update）
   models.py: GuestClient / WaitingQueue / Room / RoomMember
   management command: expire_random_calls（満了処理の保険）

「対話に参加」→ POST /call/enter/ → router.push('/meeting', { room, mode: 'random', endsAt })
[app/meeting.tsx] → components/Meeting.tsx（ネイティブ）/ Meeting.web.tsx（Web）
   ├ 通話終了操作（readyToClose）→ POST /call/leave/ → router.back()
   └ endsAt 到達 → 通話を閉じて POST /call/leave/ → router.back()
```

## データモデル（`backend/matching/models.py`）

```python
class GuestClient(models.Model):
    """ログインなしの利用者。利用者識別子1つにつきゲスト用CustomUserを1つ持つ。"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="guest_client")
    client_id_hash = models.CharField(max_length=64, unique=True, db_comment="利用者識別子のSHA-256")
    created_at = models.DateTimeField(auto_now_add=True, db_comment="作成日時")


class WaitingQueue(models.Model):  # 既存モデルを変更
    user = models.OneToOneField(CustomUser, related_name="waiting", on_delete=models.CASCADE)  # FK → OneToOne
    created_at = models.DateTimeField(auto_now_add=True, db_comment="作成日時")  # FIFOの順序・タイムアウトの起点

    class Meta:
        ordering = ["created_at", "id"]


class Room(models.Model):  # 既存モデルを変更（users の M2M を RoomMember に置き換え）
    class Status(models.TextChoices):
        ACTIVE = "active"
        ENDED = "ended"

    class EndReason(models.TextChoices):
        ALL_LEFT = "all_left"   # 全メンバーが満了前に通話終了した
        EXPIRED = "expired"     # 有効時間の満了

    room_name = models.CharField(max_length=64, unique=True, db_comment="Jitsiのルーム名")  # "pd-" + secrets.token_hex(16)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    end_reason = models.CharField(max_length=10, choices=EndReason.choices, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_comment="作成日時")
    expires_at = models.DateTimeField(db_comment="有効期限")  # created_at + ROOM_TTL
    ended_at = models.DateTimeField(null=True, blank=True)


class RoomMember(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="room_memberships")
    is_active = models.BooleanField(default=True)            # このメンバー行が現在ユーザーを拘束しているか
    joined_at = models.DateTimeField(null=True, blank=True)  # 初回入室
    left_at = models.DateTimeField(null=True, blank=True)    # 満了前の通話終了

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["room", "user"], name="unique_room_member"),
            # 1ユーザーが同時に複数の未終了グループに属さない（requirements ストーリー3-6）
            models.UniqueConstraint(fields=["user"], condition=models.Q(is_active=True), name="one_active_room_per_user"),
        ]
```

定数は `matching/constants.py` の1箇所にまとめる（requirements ストーリー5-1、制約・前提条件）。

```python
GROUP_SIZE = 4
QUEUE_TIMEOUT = timedelta(minutes=5)
ROOM_TTL = timedelta(minutes=30)
ROOM_NAME_PREFIX = "pd-"
```

### ユーザーの状態の導出

状態フィールドを持たず、行の有無から導出する（`services.get_state(user)`）。

| 状態 | 条件 |
| --- | --- |
| 待機中（`waiting`） | `WaitingQueue` の行がある |
| マッチング済み（`matched`） | `is_active=True` の `RoomMember` があり、`joined_at` が `null` |
| 通話中（`in_call`） | `is_active=True` の `RoomMember` があり、`joined_at` が設定済み |
| 未参加（`none`） | 上記のいずれでもない |

- 「通話中」は「一度入室し、まだ通話終了操作をしていない」ことを表す。通話画面をいったん閉じて Home に戻った場合も「通話中」のままで、再入室できる（ストーリー4-8）
- `is_active` はグループ終了時に全メンバー分まとめて `False` にするほか、ユーザー自身が通話終了操作をした時点でもその行だけ `False` にする。これにより退室したユーザーはすぐ「未参加」に戻り、再び待機列に並べる（ストーリー5-2、5-3）

### 既存フィールドの廃止

`accounts.CustomUser.matching_status` と `accounts/choices.py` の `UserMatchingStatus` を削除する。参照箇所は `matching/views.py`・`matching/signals.py`（いずれも作り直し・削除）と `accounts/views.py` の `UserView`（レスポンスから `matching_status` を外す）のみ。

## 利用者識別子（ログインなし）

- **発行**: `POST /api/matching/client/` がサーバー側で `secrets.token_urlsafe(32)` を生成し、ゲスト用 `CustomUser`（`username = "guest-" + secrets.token_hex(16)`、`set_unusable_password()`）と `GuestClient` を作成して、利用者識別子を返す。DB には SHA-256 ハッシュのみを保存する
  - クライアントに値を生成させない理由: 推測しやすい値や他人の値を指定されることを防ぐため
- **送信**: 以降の `matching` の API はすべて `X-Client-Id: <利用者識別子>` ヘッダーを付ける
- **認証クラス** `matching/authentication.py` の `ClientIdAuthentication`: ヘッダーをハッシュ化して `GuestClient` を引き、`(guest.user, None)` を返す。ヘッダーが無い・該当なしなら認証失敗（401。`authenticate_header()` を実装して 403 ではなく 401 にする）
- **保存（フロントエンド）**: `lib/client-id.ts` が `@react-native-async-storage/async-storage`（既に依存に含まれており、Web では `localStorage` を使う）に保存する。初回や 401 を受けたときは発行し直して保存し、元のリクエストを1回だけ再試行する（DB を作り直した場合などへの対応）
- ゲスト用ユーザーはパスワードが使えないため、既存の `POST /api/auth/login/` ではログインできない

## API設計（`/api/matching/`）

発行 API を除き、すべて `ClientIdAuthentication` + `IsAuthenticated`。

| メソッド | パス | 概要 |
| --- | --- | --- |
| POST | `client/` | 利用者識別子を発行する（認証不要、IP ごとに `30/hour` のレート制限） |
| GET | `status/` | 自分の状態を返す。先頭で `expire_stale()` を実行する |
| POST | `join/` | 待機列に参加する。既に待機中なら重複追加せず200で現在の状態を返す。マッチング済み・通話中なら409 |
| POST | `cancel/` | 待機を取りやめる。待機中でなければ409 |
| POST | `call/enter/` | 入室を記録し「通話中」にする（`joined_at` は初回のみ設定）。未所属なら404、グループ終了済みなら410 |
| POST | `call/leave/` | 通話終了を記録する。未所属・終了済みなら何もせず200 |

既存の `GET join/`・`GET cancel/` は削除する。

`GET status/`（および join / cancel / enter の成功レスポンス）の形式:

```json
{
  "status": "waiting",                   // none | waiting | matched | in_call
  "server_time": "2026-09-19T06:00:00Z",
  "waiting": { "since": "...", "expires_at": "..." },        // waiting のときのみ
  "room": { "room_name": "pd-9f1c...", "expires_at": "..." } // matched / in_call のときのみ
}
```

- 残り時間の表示（ストーリー2-8、4-7）はサーバー時刻を基準にする。フロントエンドは `server_time` と端末時刻の差を補正に使う
- ルーム名を返すのは本人の状態としてのみで、他人のグループやルーム名を指定して取得する API は設けない

エラー:

| 状況 | ステータス |
| --- | --- |
| `X-Client-Id` なし・不正 | 401 |
| join: マッチング済み・通話中 | 409（本文に現在の状態を含める） |
| cancel: 待機中でない | 409（同上） |
| call/enter: 未終了グループに属していない | 404 |
| call/enter: グループが終了済み（満了） | 410 |

## サービス層（`matching/services.py`）

ビューはリクエストの解釈とレスポンスの整形だけを行い、状態を変える処理はすべて以下に集約する。各関数は `transaction.atomic()` 内で対象行を `select_for_update()` してから判定・更新する。

- `issue_client()`: ゲスト用ユーザーと `GuestClient` を作成し、平文の利用者識別子を返す
- `get_state(user)`: 上表のとおり状態を導出する
- `join_queue(user)`: `is_active=True` の `RoomMember` があれば `AlreadyInRoom`（→409）。`WaitingQueue.objects.get_or_create(user=user)` の後、`try_form_group()` を呼ぶ
- `cancel_queue(user)`: 自分の `WaitingQueue` 行を `select_for_update()` で取得して削除する。取得できなければ（同時にマッチング成立・タイムアウトで消えていた場合を含む）`NotWaiting`（→409）。**元の行を必ず削除する**（既知の課題の修正）
- `try_form_group()`: `WaitingQueue.objects.select_for_update().order_by("created_at", "id")[:GROUP_SIZE]` を取得し、`GROUP_SIZE` 件未満なら何もしない。揃っていれば `Room`（`room_name = ROOM_NAME_PREFIX + secrets.token_hex(16)`、`expires_at = now + ROOM_TTL`）と `RoomMember` ×4 を作成し、対象の待機行を削除する。制約違反（`IntegrityError`）はトランザクションごとロールバックされ、待機列はそのまま残る
- `enter_call(user)`: 自分の `is_active=True` の `RoomMember` を `select_for_update()`（`room` を `select_related`）で取得する。なければ `NotInRoom`（→404）。`expires_at` を過ぎていればその場で `end_room(EXPIRED)` を確定させてから `RoomEnded`（→410）。`joined_at` が未設定なら設定する
- `leave_call(user)`: 同様に取得し、なければ何もしない。`left_at = now`、`is_active = False` を設定する。`is_active=True` のメンバーが残っていなければ `end_room(room, ALL_LEFT)`。満了済みなら `left_at` を立てずに `end_room(EXPIRED)` を行う
- `end_room(room, reason)`: `status = ENDED`、`end_reason`、`ended_at` を設定し、全メンバー行を `is_active = False` にする
- `expire_stale(now)`: (1) `created_at <= now - QUEUE_TIMEOUT` の `WaitingQueue` を削除する（ストーリー2-5）。(2) `status=ACTIVE` かつ `expires_at <= now` の `Room` を1件ずつ `end_room(EXPIRED)` する（ストーリー5-5、5-6、5-9）。どちらも呼び出したユーザーに限らず全体を対象にする

### 同時実行の考え方

- 「取りやめとマッチング成立が同時」（ストーリー2-4）、「タイムアウトと成立が同時」（2-7）: どちらも `WaitingQueue` 行のロックで順番に処理される。先に成立した側が待機行を削除するので、後から来た取りやめ・タイムアウトは対象行を取得できず何もしない。逆の順なら成立側は4件揃わず何もしない
- 「通話終了の記録と満了が同時」: `Room` 行のロックで順番に処理される
- 1ユーザーが複数の未終了グループに属すること（3-6、3-7）は、`one_active_room_per_user` 制約と `WaitingQueue.user` の OneToOne 制約で DB レベルでも防ぐ
- **SQLite（開発環境）では `select_for_update()` は無効**だが、書き込みトランザクションが DB ファイル単位で直列化されるため上記の性質は保たれる。競合時は片方が `database is locked` で失敗しうるため、ビューでは `OperationalError` を 503 として返し、フロントエンドは次のポーリング・再操作で回復する

## 期限切れ処理の方式

常駐ワーカーを持たないため、**遅延評価 + 管理コマンド**の二段構えにする。

1. **遅延評価**: `GET status/` と `POST join/`・`POST call/enter/` の先頭で `expire_stale()` を実行する。待機中・マッチング済みのクライアントは3秒間隔でポーリングするため、タイムアウトは最大3秒ほど遅れて処理される
2. **管理コマンド** `python manage.py expire_random_calls`: `expire_stale()` を1回実行する。誰もポーリングしていないグループを終わらせるための保険。開発環境では手動実行、本番では外部スケジューラから1分間隔で起動する。実行されなくても、次に誰かが `status` を呼んだ時点で処理される

通話画面側の満了（ストーリー5-7）は、サーバーへの問い合わせではなく、入室時に受け取った `expires_at` に基づくタイマーで通話を閉じる（後述）。サーバー側の `Room` の終了は上記の遅延評価で確定する。

## フロントエンド設計

### 設定

- `frontend/.env` に `EXPO_PUBLIC_API_BASE_URL=http://localhost:8000` を追加する
- Android（エミュレータ・実機）からは `adb reverse tcp:8000 tcp:8000` で `localhost:8000` をホストのバックエンドにつなぐ（Metro の 8081 と同じ方式。`scripts/force-localhost-reconnect.ps1` 参照）。これにより `ALLOWED_HOSTS` を変えずに済む

### 新規ファイル

リポジトリ直下の `.gitignore`（Python 用テンプレート）が `lib/` を無視するため、`!frontend/lib/` を追加して追跡対象に戻す。

| ファイル | 役割 |
| --- | --- |
| `lib/client-id.ts` | 利用者識別子の読み出し・発行・保存（AsyncStorage、キー `randomCall.clientId`） |
| `lib/api-client.ts` | `fetch` のラッパー。`EXPO_PUBLIC_API_BASE_URL` と `X-Client-Id` を付与し、401 のとき利用者識別子を発行し直して1回だけ再試行する |
| `lib/random-call.ts` | `getStatus` / `join` / `cancel` / `enterCall` / `leaveCall` と、レスポンスの型（`RandomCallState`） |
| `hooks/use-random-call.ts` | Home画面用の状態管理フック（下記） |

### `useRandomCall()`（`hooks/use-random-call.ts`）

- `useFocusEffect`（expo-router）で、Home画面にフォーカスが当たるたびに `getStatus()` を1回呼ぶ（アプリ再起動や通話画面からの復帰時の状態反映。ストーリー4-8）
- フォーカス中かつ状態が `waiting` / `matched` / `in_call` の間は3秒間隔でポーリングする（ストーリー3-8 の「5秒以内」）。`none` の間とフォーカスが外れている間は止める
- **タイムアウトの検知**: 直前の状態が `waiting` で、ユーザーが取りやめ操作をしていないのに `none` になったら、タイムアウトとして「相手が見つからなかった」を表示する（ストーリー2-6）。`waiting` から `none` になる経路は取りやめとタイムアウトだけなので、サーバー側に「直前の結果」を保持しなくて済む
- 1秒ごとに再描画して残り時間を更新する。基準はサーバーの `expires_at` と `server_time` から求めた時刻差補正
- 返す値: `state`、`remainingMs`、`notice`（タイムアウト・エラー表示用）、`busy`、`join()`、`cancel()`、`enter()`

### Home画面（`app/(tabs)/index.tsx`）

見た目の構成（ヘッダー、「今日の問い」カード、`callButtonWrapper` の位置）は変えず、ボタン部分だけを状態に応じて切り替える。

| 状態 | 表示 |
| --- | --- |
| `none` | 既存の「対話をはじめる」ボタン（`View` → `Pressable` に変更し `join()` を呼ぶ）。`notice` があればボタンの上に表示 |
| `waiting` | 「相手を探しています（残り m:ss）」と「待機をやめる」ボタン（`cancel()`） |
| `matched` / `in_call` | 「メンバーが揃いました（残り約N分）」と「対話に参加」ボタン（`enter()` の後に通話画面へ遷移） |

- 「一人で対話を開始する」ボタンと `handleStartAlone` は変更しない（ストーリー1-8）
- 「対話に参加」: `enterCall()` が成功したら `router.push({ pathname: '/meeting', params: { room: room_name, mode: 'random', endsAt: String(<端末時刻に補正した満了時刻(ms)>) } })`。「一人で対話を開始する」と同じ遷移の仕方である

### 通話画面（`app/meeting.tsx`、`components/Meeting*.tsx`）

- `app/meeting.tsx`: `room` に加えて任意の `mode`・`endsAt` を受け取る。`mode === 'random'` のときだけ、`Meeting` に `onClose`（`leaveCall()` を投げっぱなしで呼ぶ）と `endsAt` を渡す。パラメータが無い場合（「一人で対話を開始する」）の挙動は今までと同じ
- `components/Meeting.tsx`（ネイティブ）・`components/Meeting.web.tsx`（Web）に任意の props を追加する
  - `onClose?: () => void`: 通話終了操作（ネイティブの `onReadyToClose`、Web の `readyToClose` イベント）で、`router.back()` の前に呼ぶ
  - `endsAt?: number`: その時刻に達したら通話を閉じる（ネイティブは `jitsiMeeting.current?.close()`、Web は `api.dispose()`）。その後 `onClose` を呼んで `router.back()` する
  - `close()` が `onReadyToClose` をもう一度発火させる場合に備え、`closedRef` で `router.back()` と `onClose` が1回しか実行されないようにする
- Jitsi のサーバー URL・config・flags、表示名（アプリからは設定しない。ストーリー4-9）は既存のまま

## 主要フロー

1. **初回**: Home の「対話をはじめる」→ `lib/client-id.ts` に識別子がないので `POST client/` → 保存 → `POST join/` → `waiting` → ポーリング開始
2. **マッチング**: 4人目の `join/` の中で `try_form_group()` がグループを作る → 他の3人は次のポーリング（3秒以内）で `matched` を受け取る → 「対話に参加」
3. **入室**: `POST call/enter/` → `in_call` → `/meeting?room=pd-...&mode=random&endsAt=...` → 既存の Jitsi 画面で入室
4. **途中退室**: 通話終了操作 → `onClose` → `POST call/leave/` → `router.back()` → Home で `none`（再度参加できる）。全員が退室したら `end_room(ALL_LEFT)`
5. **満了**: `endsAt` で通話画面が自動で閉じる → Home に戻る。サーバーは次の `status` / 管理コマンドで `end_room(EXPIRED)`、残っていたメンバーは `none`
6. **タイムアウト**: 待機から5分 → 次の `status` で待機行が削除され `none` → フロントエンドが `waiting → none` を検知して「相手が見つからなかった」を表示

## 検討した代替案 (Alternatives Considered)

| 案 | 概要 | 採用しなかった理由 |
| --- | --- | --- |
| `CustomUser.matching_status` を拡張して使い続ける | `NONE/WAITING/MATCHED/IN_CALL` を保存する | 状態フィールドと待機列・グループ行の二重管理になり、実際に「成立時に `NONE` に戻る」不整合が起きている。行の有無から導出すれば矛盾が起きない |
| `matching` のモデルが利用者識別子を直接持つ（`CustomUser` を使わない） | `WaitingQueue.client_id` などにする | 既存の `CustomUser` への外部キー構成を崩すことになり、将来ログインを入れるときに識別子とアカウントを付け替える作業が全モデルに及ぶ。ゲスト用 `CustomUser` なら、将来は `GuestClient` を正式アカウントに結び付けるだけで済む |
| 利用者識別子をクライアントで生成する（UUID） | 発行 API が不要 | 他人の値や推測しやすい値を指定されうる。サーバー発行 + ハッシュ保存のほうが安全で、発行 API の実装コストも小さい |
| 利用者識別子の代わりに、ゲスト用ユーザーの JWT を発行する | 既存の `JWTAuthentication` をそのまま使える | アクセストークンの有効期限（12時間）で切れるため、リフレッシュ処理か期限切れ後の作り直しが必要になり、作り直すと別人扱いになる。要件の「再起動しても同じユーザー」を満たすには期限のない識別子のほうが単純 |
| `post_save` シグナルでグループ化（既存方式） | 待機行の保存時に4人揃ったか判定する | トランザクション境界・ロックを制御しづらく、同時参加で同一ユーザーが複数グループに入りうる（既知の課題） |
| WebSocket（Django Channels）でマッチング成立をプッシュ | 即時に反映できる | ASGI サーバー・チャネルレイヤーの追加が必要。要件は「5秒以内」で、3秒ポーリングで満たせる |
| Celery 等で期限切れを処理 | 正確な時刻に処理できる | ブローカー等の新規インフラが必要。遅延評価 + 管理コマンドで要件を満たせる |
| タイムアウトの結果をサーバーが保持して返す（`last_result`） | 取りこぼしなく通知できる | 状態の保存場所が増える。`waiting → none` の変化をクライアントで検知すれば足り、取りこぼしても「未参加」に戻るだけで実害がない |
| 通話画面でも `status` をポーリングして満了を検知する | サーバーの判断に完全に従う | Jitsi の画面を表示中に通信を増やすことになる。入室時に受け取った `expires_at` によるタイマーで十分正確 |

## セキュリティ・プライバシーへの影響

- **利用者識別子はパスワード相当の秘密値**である。十分な長さのランダム値（`token_urlsafe(32)`）とし、DB には SHA-256 ハッシュだけを保存する。ログにも平文を出さない
- 認可の境界は「識別子を持っている人 = そのゲストユーザー」である。ルーム名・状態は本人のものしか返さず、他人の ID を指定する API は存在しない
- `POST client/` は誰でも呼べるため、DRF の `ScopedRateThrottle` で IP ごとに `30/hour` に制限し、ゲストユーザーの大量作成を抑える（`REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]` に `matching_client` を追加）
- 状態を変える API はすべて `POST`。`matching` のビューはセッション認証を使わないため CSRF の対象外
- CORS: `django-cors-headers` を導入し、`CORS_ALLOWED_ORIGINS` は環境変数（既定 `http://localhost:8081`、Expo Web の開発サーバー）で指定する。`X-Client-Id` を許可ヘッダーに追加する（`CORS_ALLOW_HEADERS = (*default_headers, "x-client-id")`）。認証に Cookie を使わないので `CORS_ALLOW_CREDENTIALS` は不要
- Jitsi のルーム名は `pd-` + 128 bit の乱数で推測できない。ただし公開インスタンス `meet.jit.si` 上のルームであり、ルーム名を知っていれば誰でも入れる点は既存の「一人で対話を開始する」と同じ（Non-Goals）
- 通話相手に開示されるのは、各自が Jitsi 上で入力した表示名だけ（ゲスト用ユーザー名は画面にもレスポンスにも出さない）

## パフォーマンス・スケーラビリティへの影響

- ポーリングは待機中・マッチング済み・通話中に Home を開いている利用者だけが3秒間隔で行う。`status` の処理は小さなクエリ数回と `expire_stale()`（インデックス付きの範囲検索）で、現時点の想定規模（同時に数十人程度）では問題にならない
- `expire_stale()` を毎回実行すると、SQLite では書き込みロックの競合が起きやすくなる。対象行がない場合は書き込みを行わない（削除・更新の前に存在確認する）ことで、ロックを取る回数を抑える
- 利用者が増えた場合の対策（WebSocket 化、PostgreSQL への移行、ポーリング間隔の調整）は必要になった時点で検討する

## オブザーバビリティ

サービス層で主要イベントをログに出す（`structlog.get_logger("matching")`。`pyproject.toml` の Ruff 設定で `logging.getLogger` は禁止されている）。出力する項目はゲストユーザーの ID とルームの ID のみとし、利用者識別子・ルーム名は出さない。

- `client_issued` / `queue_joined` / `queue_cancelled` / `queue_timed_out`（件数）/ `room_formed`（メンバーID）/ `call_entered` / `call_left` / `room_ended`（理由）
- 成功指標（待ち時間の中央値、タイムアウト率）は `WaitingQueue` がタイムアウト時に削除されるため、このログから集計する

## テスト戦略

**バックエンド（`matching/tests.py`、`python manage.py test matching`）**

- サービス層: 参加・重複参加・取りやめ（元の行が消えること）・4人目でのグループ化・FIFO の順序・5人目は次のグループ待ち・入室・再入室（`joined_at` が変わらない）・退室・全員退室で `ALL_LEFT`・満了で `EXPIRED` と全員 `none`・タイムアウト。時刻は `unittest.mock.patch` で `timezone.now` を差し替える
- 競合の再現: 「成立後に取りやめ → 409」「成立後のタイムアウト処理で何も起きない」など、順番を入れ替えた呼び出しで不整合が起きないことを確認する
- 制約: `one_active_room_per_user` に違反する作成が `IntegrityError` になること
- API: 各エンドポイントのステータスコード、`X-Client-Id` なし・不正で 401、他人の状態が返らないこと、`GET` で join/cancel できないこと、発行 API のレート制限
- 認証クラス: ハッシュでの照合、平文が DB に保存されないこと

**フロントエンド**

- 自動テスト基盤がないため `npm run lint` のみ自動で確認し、動作は手動で確認する
- 手動確認の手順は `manuals/random-call-testing.md` にまとめる。4つの別々の利用者識別子が必要になるため、別ブラウザ・シークレットウィンドウ・Android エミュレータを組み合わせる。人数が足りない場合のために、開発用の管理コマンド `python manage.py add_dummy_waiters <人数>`（ダミーのゲストを待機列に追加する。`DEBUG=True` のときだけ実行可能）を用意する
- 確認項目: 待機・残り時間表示・取りやめ・タイムアウト表示・4人でのマッチング・同じルームへの入室（Android と Web の混在を含む）・再入室・途中退室・満了で通話画面が閉じる・「一人で対話を開始する」が今までどおり動く

## ロールアウト計画

- 開発段階のため段階的リリースは行わない。バックエンドとフロントエンドを同時に更新する
- マイグレーション:
  - `matching`: `WaitingQueue.user` を OneToOne に変更（既存の重複行があると失敗するため、マイグレーション内で既存の `WaitingQueue` 行を全削除する）、`Room.users` の M2M を削除して `RoomMember` を追加、`Room` に新フィールドを追加（既存の `Room` 行は `room_name` などを持たないため全削除する）、`GuestClient` を追加
  - `accounts`: `matching_status` を削除
  - 既存の待機行・ルーム行は開発用データであり、削除して問題ない
- ロールバック: マイグレーションを戻し、コードを以前のコミットに戻す。フロントエンドは `mode` パラメータを渡さなければ以前と同じ動きになる
- `requirements.txt` に `django-cors-headers` を追加する（`pip install -r requirements.txt` が必要になる旨を docs/backend.md に書く）

## リスクと対策

| リスク | 影響 | 対策 |
| --- | --- | --- |
| SQLite の書き込みロック競合（`database is locked`） | 同時操作の片方が失敗する | 503 を返し、フロントエンドは次のポーリング・再操作で回復する。期限切れ処理は対象がなければ書き込まない |
| アプリの強制終了で通話終了が記録されない | そのユーザーが「通話中」のまま残る | 満了時に `none` に戻る（ストーリー5-9）。全員がそうなった場合も満了でグループは終わる |
| 端末の時計のずれ | 残り時間表示・自動終了の時刻がずれる | `server_time` との差で補正する |
| 「一人で対話を開始する」で通話中にマッチングが成立する | その通話中はマッチングに気づけない | ストーリー1-8 によりボタンは変えない。Home に戻った時点で `matched` が表示され、気づかなければ満了で解消される |
| `@react-native-async-storage/async-storage@1.24.0` が古い | New Architecture 環境で不具合が出る可能性 | Jitsi SDK の依存として既に導入・リンク済みのため、バージョンは変えずに使う（docs/frontend.md の方針）。問題が出たら手動確認の段階で対処する |
| `meet.jit.si` の仕様変更（モデレーターのログイン要求など） | 入室できない | 既存の「一人で対話を開始する」と同じリスクであり、本スペックでは扱わない（[self-host-jitsi-server](../self-host-jitsi-server/requirements.md)） |

## 未解決事項 (Open Questions)

現時点でなし。
