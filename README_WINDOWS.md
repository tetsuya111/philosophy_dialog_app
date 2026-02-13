# 🎥 WebRTC Video Conference - Windows セットアップガイド

Windows環境でのセットアップと起動方法を説明します。

## 📋 必要要件

### 1. Python のインストール

1. [Python公式サイト](https://www.python.org/downloads/) にアクセス
2. **Python 3.8以上** をダウンロード
3. インストール時に **"Add Python to PATH"** にチェック ✅
4. コマンドプロンプトで確認:
   ```cmd
   python --version
   ```

### 2. Node.js のインストール

1. [Node.js公式サイト](https://nodejs.org/) にアクセス
2. **LTS版（推奨）** をダウンロード
3. インストール実行
4. コマンドプロンプトで確認:
   ```cmd
   node --version
   npm --version
   ```

## 🚀 クイックスタート

### 方法1: シンプル起動（推奨）

1. **エクスプローラーで `start.bat` をダブルクリック**

これだけで完了です！自動的に:
- バックエンドサーバーが起動
- フロントエンドサーバーが起動
- ブラウザが開きます

### 方法2: コマンドプロンプトから起動

1. **コマンドプロンプトを開く**
   - `Win + R` → `cmd` → Enter

2. **プロジェクトフォルダに移動**
   ```cmd
   cd C:\path\to\webapp
   ```

3. **起動スクリプトを実行**
   ```cmd
   start.bat
   ```

### 方法3: 詳細表示付き起動

より詳しい起動ログを見たい場合:
```cmd
start-dev.bat
```

## 🛑 サーバーの停止

### 方法1: 簡単な停止
`stop.bat` をダブルクリック

### 方法2: コマンドから停止
```cmd
stop-dev.bat
```

### 方法3: 手動で停止
サーバーのコマンドプロンプトウィンドウで `Ctrl + C` を押す

## 📁 スクリプトファイル一覧

| ファイル | 説明 | 用途 |
|---------|------|------|
| `start.bat` | シンプル起動 | 初心者向け・日常使用 |
| `start-dev.bat` | 詳細起動 | 開発者向け・トラブルシューティング |
| `stop.bat` | シンプル停止 | 素早い停止 |
| `stop-dev.bat` | 詳細停止 | 確実な停止 |

## 🌐 アクセスURL

サーバー起動後、以下のURLにアクセスできます:

- **フロントエンド（アプリ画面）**: http://localhost:3000
- **バックエンドAPI**: http://localhost:8000
- **Django管理画面**: http://localhost:8000/admin

## 🔧 初回セットアップ

### 1. 依存関係のインストール

#### バックエンド（Python）
```cmd
cd backend
pip install -r requirements.txt
cd ..
```

#### フロントエンド（Node.js）
```cmd
cd frontend
npm install
cd ..
```

### 2. データベースの初期化
```cmd
cd backend
python manage.py migrate
cd ..
```

**注意**: `start.bat` または `start-dev.bat` を実行すると、これらは自動的に実行されます。

## ❗ トラブルシューティング

### エラー: "Python is not recognized"
**原因**: Pythonがインストールされていないか、PATHに追加されていません

**解決策**:
1. Pythonを再インストール
2. インストール時に "Add Python to PATH" にチェック
3. または、環境変数を手動で設定:
   - `Win + X` → システム → システムの詳細設定
   - 環境変数 → Path → 編集
   - Python のパスを追加（例: `C:\Python312`）

### エラー: "node is not recognized"
**原因**: Node.jsがインストールされていないか、PATHに追加されていません

**解決策**:
1. Node.jsを再インストール
2. コマンドプロンプトを再起動

### エラー: "Port 8000 is already in use"
**原因**: ポート8000が既に使用されています

**解決策**:
```cmd
REM ポートを使用しているプロセスを確認
netstat -ano | findstr :8000

REM プロセスを強制終了（PIDを確認して実行）
taskkill /F /PID [プロセスID]

REM または stop.bat を実行
stop.bat
```

### エラー: "Port 3000 is already in use"
**原因**: ポート3000が既に使用されています

**解決策**:
```cmd
REM ポートを使用しているプロセスを確認
netstat -ano | findstr :3000

REM プロセスを強制終了（PIDを確認して実行）
taskkill /F /PID [プロセスID]

REM または stop.bat を実行
stop.bat
```

### サーバーが起動しない
1. **依存関係の再インストール**:
   ```cmd
   cd backend
   pip install -r requirements.txt
   cd ..\frontend
   npm install
   cd ..
   ```

2. **ポートの解放**:
   ```cmd
   stop.bat
   ```
   少し待ってから再度起動

3. **ログの確認**:
   `start-dev.bat` を使用して詳細なエラーメッセージを確認

## 💡 便利なTips

### 1. デスクトップショートカットの作成

1. `start.bat` を右クリック
2. 「ショートカットの作成」
3. ショートカットをデスクトップに移動
4. 右クリック → プロパティ → アイコンの変更（お好みで）

### 2. 管理者権限で実行

ポート関連の問題がある場合:
1. `start.bat` を右クリック
2. 「管理者として実行」

### 3. 自動起動設定

Windowsスタートアップに追加する場合:
1. `Win + R` → `shell:startup` → Enter
2. `start.bat` のショートカットをこのフォルダに配置

### 4. ログファイルの確認

サーバーウィンドウで出力されるログをファイルに保存:
```cmd
cd backend
python manage.py runserver > server.log 2>&1
```

## 📊 システム要件

| 項目 | 最小要件 | 推奨要件 |
|-----|---------|---------|
| OS | Windows 10 | Windows 10/11 |
| Python | 3.8+ | 3.10+ |
| Node.js | 14+ | 18+ LTS |
| RAM | 4GB | 8GB+ |
| ディスク空き容量 | 2GB | 5GB+ |

## 🔒 セキュリティ注意事項

- **開発環境専用**: このスクリプトは開発用です
- **本番環境では使用しない**: 本番環境では適切なWebサーバー（Nginx, Apache）を使用してください
- **ファイアウォール**: 必要に応じてWindowsファイアウォールの設定を確認してください

## 📚 関連ドキュメント

- [メインREADME](README.md) - 全体的な説明
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - プロジェクト概要
- [Django Documentation](https://docs.djangoproject.com/)
- [React Documentation](https://react.dev/)

## 🆘 サポート

問題が解決しない場合:
1. GitHubのIssueを作成
2. エラーメッセージの全文を含める
3. Windows バージョンを記載
4. Python と Node.js のバージョンを記載

---

**Enjoy coding on Windows! 🎉**
