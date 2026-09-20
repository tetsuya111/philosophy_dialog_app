# ランダムコールのフロントエンド実装（tasks.md タスク9〜11）

## 何を行ったか

- `frontend/.env` に `EXPO_PUBLIC_API_BASE_URL=http://localhost:8000` を追加。
- `frontend/lib/` を新設: `client-id.ts`（利用者識別子を AsyncStorage に保存）、`api-client.ts`（`X-Client-Id` 付き fetch、401 時は識別子を発行し直して1回だけ再試行）、`random-call.ts`（API関数と型）。
- `hooks/use-random-call.ts`: フォーカス時の状態取得、3秒ポーリング、`waiting → none` によるタイムアウト検知、サーバー時刻による補正、古いポーリング結果で上書きしない制御。
- `app/(tabs)/index.tsx`: 見た目だけだった「対話をはじめる」を `Pressable` にし、状態に応じて「待機をやめる」「対話に参加」と残り時間を表示。「一人で対話を開始する」は変更なし。
- `app/meeting.tsx`: `mode=random` のときだけ `onClose`（`leaveCall()`）と `endsAt` を `Meeting` に渡す。
- `components/Meeting.tsx` / `Meeting.web.tsx`: 任意 props `onClose` / `endsAt` を追加（`closedRef` で二重実行を防止）。
- リポジトリ直下の `.gitignore` が Python 用に `lib/` を無視していたため、`!frontend/lib/` を追加。
- 変更・追加したファイルは ESLint・`tsc` ともエラーなし（確認のため Linux 環境で `yarn install --ignore-scripts --ignore-engines` を実行）。

## なぜ行ったか

既存の Home 画面・通話画面を流用して、ランダムコール（待機・マッチング・入室・退室・満了）をフロントエンドから使えるようにするため。

## 補足

実機・ブラウザでの動作確認（tasks.md タスク13）は未実施。手順は [manuals/random-call-testing.md](../manuals/random-call-testing.md)。
