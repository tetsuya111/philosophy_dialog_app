# ランダムコールの動作確認手順

Home画面の「対話をはじめる」から、待機列への参加 → 4人でのマッチング → グループ専用の Jitsi ルームでの通話までを手元で確認するための手順。仕様は [.kiro/specs/random-call/](../.kiro/specs/random-call/requirements.md) を参照。

## 前提・制約

- ログインは不要。利用者は、初回にバックエンドが発行する**利用者識別子**（端末の AsyncStorage、Web 版ではブラウザの localStorage に保存）で見分けられる。**4人でマッチングするには、識別子が別々のクライアントが4つ必要**。
  - 同じブラウザの通常ウィンドウ同士は localStorage を共有するので、同じ人として扱われる。別ブラウザ（Chrome / Edge / Firefox）、シークレットウィンドウ、ブラウザのプロファイル違い、Android エミュレータを組み合わせる。
  - クライアントが足りない場合は、下記の `add_dummy_waiters` でダミーの待機者を足す。
- 通話画面そのものの確認方法（dev client のビルド、Web 版の仕組み、トラブルシューティング）は [video-call-testing.md](video-call-testing.md) を参照。
- 時間の設定は `backend/matching/constants.py` にある（待機タイムアウト5分、通話の有効時間30分）。満了の確認時は一時的に短くしてよい（確認後は戻すこと）。

## 準備

### 1. バックエンドを起動する

```bash
cd backend
pip install -r requirements.txt   # django-cors-headers を追加したため
python manage.py migrate
python manage.py runserver
```

### 2. フロントエンドの接続先を確認する

`frontend/.env` の `EXPO_PUBLIC_API_BASE_URL`（既定 `http://localhost:8000`）がバックエンドを指していることを確認する。`.env` を変えた場合は Metro を再起動する。

Android（エミュレータ・実機）から使う場合は、ホストの `localhost:8000` に届くようにする。

```bash
adb reverse tcp:8000 tcp:8000
```

`npm run android:win` などでエミュレータを再起動した後は、再度実行が必要になることがある。

### 3. フロントエンドを起動する

```bash
cd frontend
npm run web            # Web 版
npx expo run:android   # Android 版（Windows の場合は npm run android:win）
```

## 確認項目

### A. 待機・取りやめ・タイムアウト（1クライアント）

1. Home の「対話をはじめる」を押す → 「相手を探しています（残り 4:59）」と表示され、残り時間が1秒ずつ減る
2. 「待機をやめる」を押す → 「対話をはじめる」に戻る
3. もう一度参加し、5分待つ（または `QUEUE_TIMEOUT` を一時的に短くする） → 「相手が見つかりませんでした。もう一度お試しください。」が表示され、「対話をはじめる」に戻る

### B. マッチングと入室（ダミー3人 + 1クライアント）

1. クライアントで「対話をはじめる」を押して待機中にする
2. バックエンドでダミーを3人追加する

   ```bash
   python manage.py add_dummy_waiters 3
   ```

3. 5秒以内に「メンバーが揃いました（残り約30分）」と「対話に参加」が表示される
4. 「対話に参加」を押す → Jitsi の通話画面に `pd-` で始まるルーム名で入る
5. 通話画面を閉じずに Home に戻る（Android の戻る操作、Web のブラウザバック）→ 「対話に参加」が再び表示され、同じルームに再入室できる
6. 通話終了操作（Jitsi のハングアップ）をする → Home に戻り、「対話をはじめる」に戻る（途中退室。再び待機列に並べる）

ダミーは入室しないため、グループは有効時間の満了まで続く。`python manage.py expire_random_calls` を実行すると、満了したグループをその場で終了できる。

### C. 実際の4クライアントでの通話

1. 4つのクライアント（例: Chrome、Chrome のシークレットウィンドウ、Edge、Android エミュレータ）で順に「対話をはじめる」を押す
2. 4人目が押した後、5秒以内に全員に「対話に参加」が表示される
3. 全員が「対話に参加」を押し、同じルームに入って映像・音声が互いに届くことを確認する（Web 版と Android 版が混ざっていても同じルームに入れること）
4. 1人が通話終了しても、残りの3人の通話は続く

### D. 有効時間の満了

1. `backend/matching/constants.py` の `ROOM_TTL` を一時的に `timedelta(minutes=2)` などにしてバックエンドを再起動する
2. B または C の手順で入室し、そのまま待つ → 満了時刻に通話画面が自動で閉じて Home に戻り、「対話をはじめる」が表示される
3. 確認後、`ROOM_TTL` を `timedelta(minutes=30)` に戻す

### E. 既存機能

- 「一人で対話を開始する」が今までどおり動く（`solo-` で始まるルーム名で単独入室し、通話終了で Home に戻る）

## トラブルシューティング

| 症状 | 確認すること |
| --- | --- |
| 「対話をはじめる」で「通信に失敗しました」 | バックエンドが起動しているか。Android なら `adb reverse tcp:8000 tcp:8000` を実行したか。`EXPO_PUBLIC_API_BASE_URL` が正しいか |
| Web 版だけ失敗し、ブラウザのコンソールに CORS エラー | Expo Web のオリジン（既定 `http://localhost:8081`）がバックエンドの `CORS_ALLOWED_ORIGINS` に含まれているか。ポートが違う場合は環境変数で指定して `runserver` し直す |
| 別ブラウザのつもりが同じ人として扱われる | 同じブラウザ・同じプロファイルの通常ウィンドウは localStorage を共有する。別ブラウザかシークレットウィンドウを使う |
| DB を作り直した後に動かない | 自動で識別子を発行し直すため、通常は操作をやり直せば回復する |
| 状態を初期化したい | `python manage.py flush`（開発DBの全データを削除する） |
