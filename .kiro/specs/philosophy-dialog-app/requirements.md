# 全体要件定義書（現状実装のリバースエンジニアリング）

> **位置づけ**: このドキュメントは、新機能の設計に先立って書く通常の `requirements.md` とは異なり、2026-09-05時点の実装（`backend/`・`frontend/`）を読んで逆算的に作成した、アプリ全体のベースライン要件定義書である。「あるべき姿」ではなく「現状動作する仕様」を記述する。実装を変更した際はこのドキュメントも追随して更新すること。

## 背景・課題（Working Backwards）

哲学対話（哲学カフェ的な対話）をしたい人同士を、知人関係に依らずランダムに引き合わせる場を提供したい。対面イベントの運営コストなしに、アプリ経由でユーザーを自動的にグルーピングし、ビデオ通話上で対話を始められるようにする。

## スコープ / Non-Goals

現状実装に基づくスコープ:

- ユーザー登録・ログイン・ログアウト・アカウント削除（`backend/accounts/`）
- ランダムな待機列ベースのグループマッチング（`backend/matching/`）
- Jitsi Meetによるビデオ通話画面（`frontend/components/Meeting.tsx`）

現状実装されていない（Non-Goals、または未着手）:

- マッチング結果（`Room`）とビデオ通話画面の連携（下記「既知の課題」参照）。現状「一人で対話を開始する」ボタンで生成される自動採番のルーム名で参加する単独利用のみ実装されており、マッチングで組まれた複数人のグループを同じルームに導く導線はない。
- テキストチャット、対話ログの保存・閲覧
- ユーザーのプロフィール編集（表示名以外の属性、アイコン等）
- マッチング条件の指定（テーマ・興味関心によるフィルタリング等）
- 通知（プッシュ通知等でのマッチング成立通知）
- 管理者向け機能（Django管理サイトの利用を除く）
- 決済・課金
- 本番運用を想定した設定管理（環境変数化、CORS設定等。[docs/backend.md](../../../docs/backend.md)の「設定」参照）

## 成功指標

現時点でアプリ内に計測の仕組みは実装されておらず、成功指標は定義されていない（要検討）。

## 機能要件

### アカウント管理（`backend/accounts/`）

**ユーザーストーリー**: As a 未登録ユーザー, I want ユーザー名とパスワードでアカウントを登録したい, so that アプリの認証が必要な機能を使えるようになる。

- THE SYSTEM SHALL `POST /api/auth/register/` で受け取った `username`/`password` から新規ユーザーを作成する（認証不要で呼び出せる）。
- THE SYSTEM SHALL パスワードをハッシュ化（`make_password`）した上で保存する。

**ユーザーストーリー**: As a 登録済みユーザー, I want ユーザー名とパスワードでログインしたい, so that 認証が必要なAPIを呼び出せるようになる。

- WHEN 正しい `username`/`password` で `POST /api/auth/login/` を呼び出したとき THE SYSTEM SHALL アクセストークンをhttponly Cookie（`shared/middleware.py`の`ACCESS_TOKEN_COOKIE_NAME`）として設定し、200を返す。
- IF `username`/`password` の組み合わせが不正なとき THEN THE SYSTEM SHALL 401と `{"errMsg": "ユーザーの認証に失敗しました"}` を返す。

**ユーザーストーリー**: As a ログイン中のユーザー, I want ログアウトしたい, so that 端末上のセッションを終了できる。

- WHEN `GET /api/auth/logout/` を呼び出したとき THE SYSTEM SHALL アクセストークンのCookieを削除し、200を返す。

**ユーザーストーリー**: As a ログイン中のユーザー, I want 自分のユーザー情報を確認したい, so that 現在のユーザー名やマッチング状態を把握できる。

- WHEN 認証済みユーザーが `GET /api/auth/user/me/` を呼び出したとき THE SYSTEM SHALL `userid`/`username`/`matching_status` を返す。
- IF 未認証で `GET /api/auth/user/me/` を呼び出したとき THEN THE SYSTEM SHALL 401を返す（`DEFAULT_PERMISSION_CLASSES`のグローバル設定 `IsAuthenticated` による）。

**ユーザーストーリー**: As a ログイン中のユーザー, I want 自分のアカウントを削除したい, so that アプリの利用をやめられる。

- WHEN 認証済みユーザーが `DELETE /api/auth/delete/` を呼び出したとき THE SYSTEM SHALL そのユーザー自身のアカウントを削除する。

### ランダムマッチング（`backend/matching/`）

**ユーザーストーリー**: As a ログイン中のユーザー, I want マッチングの待機列に参加したい, so that 他のユーザーとグルーピングされ対話を始められる。

- WHEN 認証済みユーザーが `GET /api/matching/join/` を呼び出し、かつ `matching_status` が `NONE` のとき THE SYSTEM SHALL そのユーザーの `WaitingQueue` エントリを作成し、`matching_status` を `WATING` に更新する。
- IF `matching_status` が `NONE` 以外（`WATING`または`JOINED`）のとき THEN THE SYSTEM SHALL 400と現在の `userid`/`status`/メッセージを返し、待機列への追加は行わない。
- WHILE `WaitingQueue` の全体件数が `WAITING_LIMIT_N`（現状4）未満である間 THE SYSTEM SHALL 新たな `Room` を作成しない。
- WHEN `WaitingQueue` の全体件数が `WAITING_LIMIT_N`（4）に達したとき THE SYSTEM SHALL 待機列の先頭4件のユーザーをまとめた `Room` を作成し、対象ユーザーの `WaitingQueue` エントリを削除し、`matching_status` を `NONE` に戻す（`matching/signals.py`の`add_to_queue`、`WaitingQueue`の`post_save`シグナルとして実行）。

**ユーザーストーリー**: As a 待機列に参加中のユーザー, I want 待機をキャンセルしたい, so that マッチングされる前に待機列から抜けられる。

- WHEN 認証済みユーザーが `matching_status` が `WATING` の状態で `GET /api/matching/cancel/` を呼び出したとき THE SYSTEM SHALL `matching_status` を `NONE` に戻す。
- IF `matching_status` が `WATING` 以外のとき THEN THE SYSTEM SHALL 400を返す。

### ビデオ通話（対話）画面（`frontend/`）

**ユーザーストーリー**: As a ユーザー, I want マッチングを介さず一人で対話（ビデオ通話）を開始したい, so that 相手を待たずに機能を試したり、一人で話したい場合に使える。

- WHEN ユーザーがHome画面（`app/(tabs)/index.tsx`）の「一人で対話を開始する」ボタンを押したとき THE SYSTEM SHALL `solo-<timestamp>-<random>`形式のルーム名を生成し、Meeting画面（`app/meeting.tsx`）に遷移して`@jitsi/react-native-sdk`の`JitsiMeeting`でそのルームに参加する。
- WHEN Jitsi Meeting画面で通話終了操作（`onReadyToClose`）が発生したとき THE SYSTEM SHALL 直前の画面（Home画面）に戻る（`expo-router`の`router.back()`）。

## 非機能要件

- THE SYSTEM SHALL ステートレスなJWT認証（`djangorestframework-simplejwt`）を用い、セッションストアを持たない。
- バックエンドの設定（`SECRET_KEY`/`DEBUG`/DB接続先）は環境変数化されておらず、`backend/backend/settings.py`にハードコードされている（[docs/backend.md](../../../docs/backend.md)参照）。
- CORS（`django-cors-headers`等）は導入されていない。
- データベースはSQLite固定。

## 既知の課題（現状コードから確認できる不整合）

- **マッチングとビデオ通話の未連携**: `matching/signals.py`が作成する`Room`は、対話に使うJitsiのルーム名や参加者への通知手段を持たず、フロントエンドの通話画面とも接続されていない。「一人で対話を開始する」ボタンで自動生成されるルーム名（`solo-<timestamp>-<random>`）は端末内で完結しており、他のユーザーと共有・合流する導線がない。
- **`cancel_matching`のキャンセル処理**: `matching/views.py`の`cancel_matching`は、既存の`WaitingQueue`エントリを削除するのではなく、新規に作成したエントリを直後に削除しており、元の待機エントリが残り続ける可能性がある。
- **ユーザー登録レスポンスの情報過多**: `CustomUserSerializer`（`accounts/serializers.py`）が`fields = "__all__"`のため、`POST /api/auth/register/`のレスポンスにハッシュ化済みパスワードを含む全フィールドが含まれる。
- **状態遷移の設計**: マッチング成立時に`matching_status`が`JOINED`ではなく`NONE`に戻る（`matching/signals.py`）。`UserMatchingStatus.JOINED`は定義されているが現状どこからも設定されていない。
- **join/cancelがGETで状態変更を行う**: `matching/urls.py`の`join/`・`cancel/`はいずれも`GET`だが、サーバー側の状態（`WaitingQueue`・`matching_status`）を変更する。

## 用語集

| 用語 | 説明 |
| --- | --- |
| `WaitingQueue` | マッチング待機列の1エントリ（`matching/models.py`） |
| `Room` | マッチングが成立したグループの単位（`matching/models.py`、ユーザーのM2M） |
| `UserMatchingStatus` | ユーザーのマッチング状態（`NONE`/`WATING`/`JOINED`、`accounts/choices.py`） |
| `WAITING_LIMIT_N` | マッチング成立に必要な待機人数（現状4、`matching/signals.py`） |
