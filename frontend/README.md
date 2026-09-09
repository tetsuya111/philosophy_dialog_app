# frontend

`philosophy_dialog_app` のフロントエンドアプリ。Expo（React Native, TypeScript, expo-router）によるモバイル/Webアプリで、Jitsi Meet SDKを使ったグループビデオ通話画面を提供する。

## セットアップ

```bash
npm install
npm run start
```

`npm run start` はExpo開発サーバーを起動する。表示されるQRコードからExpo Go/開発ビルドで実機確認するか、以下のコマンドで各プラットフォーム向けに直接起動できる。

```bash
npm run android  # Androidエミュレータ/実機
npm run ios      # iOSシミュレータ/実機
npm run web      # Webブラウザ
```

## ドキュメント

よく使うコマンド・設定・アーキテクチャ（ルーティング構成、コンポーネント配置など）は [../docs/frontend.md](../docs/frontend.md) を参照。

## Lint

```bash
npm run lint
```
