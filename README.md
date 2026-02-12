# 🎥 WebRTC Video Conference Application

WebRTC技術とJitsi Meetフレームワークを使用した、シンプルで高機能なビデオ会議アプリケーションです。

## 🌟 主な機能

- ✅ **WebRTC技術による高品質なビデオ通信**
- ✅ **最大4人まで同時参加可能**
- ✅ **ワンクリックでルーム作成・参加**
- ✅ **1コマンドで開発サーバー起動**
- ✅ **シンプルで直感的なUI/UX**

## 🏗️ アーキテクチャ

### Technology Stack

#### Frontend
- **React.js**: UI構築
- **Jitsi Meet External API**: WebRTCビデオ会議機能
- **Axios**: HTTP通信

#### Backend
- **Django 6.0**: RESTful API
- **Django REST Framework**: API開発
- **CORS Headers**: クロスオリジン対応

### プロジェクト構造

```
webapp/
├── frontend/               # React フロントエンド
│   ├── public/            # 静的ファイル
│   ├── src/
│   │   ├── components/    # Reactコンポーネント
│   │   │   ├── JitsiMeeting.js      # Jitsi会議コンポーネント
│   │   │   └── RoomList.js          # ルーム一覧コンポーネント
│   │   ├── App.js         # メインアプリ
│   │   ├── App.css        # スタイル
│   │   └── index.js       # エントリーポイント
│   └── package.json
│
├── backend/               # Django バックエンド
│   ├── backend/          # プロジェクト設定
│   │   ├── settings.py   # Django設定
│   │   └── urls.py       # URLルーティング
│   ├── webrtc/           # WebRTCアプリ
│   │   ├── views.py      # APIビュー (モック実装)
│   │   └── urls.py       # WebRTC API URLs
│   └── manage.py
│
├── start-dev.sh          # 開発サーバー起動スクリプト
├── stop-dev.sh           # 開発サーバー停止スクリプト
└── README.md
```

## 🚀 クイックスタート

### 必要要件

- Python 3.8以上
- Node.js 14以上
- npm または yarn

### インストールと起動

**1コマンドで両方のサーバーを起動:**

```bash
./start-dev.sh
```

このスクリプトは以下を自動実行します:
- Django バックエンドサーバー (ポート 8000)
- React フロントエンドサーバー (ポート 3000)
- データベースマイグレーション

### アクセス

開発サーバー起動後、以下のURLにアクセスできます:

- **フロントエンド**: http://localhost:3000
- **バックエンドAPI**: http://localhost:8000/api/webrtc/

### サーバーの停止

```bash
./stop-dev.sh
```

## 📋 API仕様 (モック実装)

### エンドポイント一覧

| メソッド | エンドポイント | 説明 |
|---------|--------------|------|
| POST | `/api/webrtc/rooms/create/` | 新しいルームを作成 |
| GET | `/api/webrtc/rooms/` | 利用可能なルーム一覧を取得 |
| GET | `/api/webrtc/rooms/{room_id}/` | 特定のルーム情報を取得 |
| POST | `/api/webrtc/rooms/{room_id}/join/` | ルームに参加 |

### レスポンス例

**ルーム作成 (POST /api/webrtc/rooms/create/)**

```json
{
  "room_id": "abc123xyz",
  "room_name": "Room-abc123xy",
  "jitsi_domain": "meet.jit.si",
  "max_participants": 4,
  "created_at": "2026-02-12T00:00:00Z"
}
```

**ルーム一覧 (GET /api/webrtc/rooms/)**

```json
{
  "rooms": [
    {
      "room_id": "mock_room_1",
      "room_name": "Room-mock_roo",
      "participants_count": 2,
      "max_participants": 4,
      "is_active": true
    }
  ]
}
```

## 🎮 使い方

### 1. ルームの作成と参加

1. アプリケーションにアクセス
2. 「🚀 新しいルームを作成して参加」ボタンをクリック
3. 自動的にルームが作成され、ビデオ会議が開始されます

### 2. 既存ルームへの参加

1. 「既存のルームに参加」セクションで利用可能なルームを確認
2. 参加したいルームの「参加」ボタンをクリック
3. ビデオ会議に参加します

### 3. ビデオ会議の操作

Jitsi Meetの標準機能を使用できます:
- 🎤 マイクのオン/オフ
- 📹 カメラのオン/オフ
- 🖥️ 画面共有
- 💬 チャット
- 📝 字幕表示
- ⚙️ 各種設定

## 🔧 開発情報

### 個別にサーバーを起動する場合

**バックエンド:**

```bash
cd backend
python -m pip install django djangorestframework django-cors-headers
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

**フロントエンド:**

```bash
cd frontend
npm install
npm start
```

### 環境変数

フロントエンドの環境変数は `frontend/.env` で設定:

```env
REACT_APP_API_URL=http://localhost:8000/api/webrtc
PORT=3000
BROWSER=none
```

### モック実装について

現在のバックエンドAPIはモック実装です。実際のルーム管理やデータ永続化は行っていません。
本番環境では以下の実装が必要です:

- データベースモデル (Room, Participant)
- JWT認証
- WebSocket (リアルタイム通信)
- Jitsi Meet自己ホスティング (オプション)

## 🧪 テスト

### APIテスト

```bash
cd backend
python manage.py test
```

### フロントエンドテスト

```bash
cd frontend
npm test
```

## 📦 デプロイ

### フロントエンド (ビルド)

```bash
cd frontend
npm run build
```

ビルドされたファイルは `frontend/build/` に生成されます。

### バックエンド (本番環境)

```bash
cd backend
python manage.py migrate
python manage.py collectstatic
gunicorn backend.wsgi:application
```

## 🔐 セキュリティ考慮事項

- **CORS設定**: 本番環境では適切なオリジンのみ許可してください
- **SECRET_KEY**: Djangoのシークレットキーを環境変数で管理してください
- **HTTPS**: 本番環境では必ずHTTPSを使用してください
- **JWT認証**: ルームへのアクセス制御を実装してください

## 🐛 トラブルシューティング

### ポートが既に使用されている

```bash
# ポート8000を使用しているプロセスを確認
lsof -ti:8000

# ポート3000を使用しているプロセスを確認
lsof -ti:3000

# または stop-dev.sh を実行
./stop-dev.sh
```

### Node modulesのエラー

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Djangoのマイグレーションエラー

```bash
cd backend
rm db.sqlite3
python manage.py migrate
```

## 📚 技術ドキュメント

- [Jitsi Meet API Documentation](https://jitsi.github.io/handbook/docs/dev-guide/dev-guide-iframe)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Documentation](https://react.dev/)

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🤝 コントリビューション

プルリクエストは大歓迎です!大きな変更を加える場合は、まずissueを開いて変更内容を議論してください。

## 📞 サポート

問題が発生した場合は、GitHubのIssueを作成してください。

---

**Enjoy your video conferencing! 🎉**
