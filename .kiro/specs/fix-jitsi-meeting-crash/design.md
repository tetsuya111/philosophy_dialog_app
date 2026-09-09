# Jitsi Meetingビデオ通話画面のレンダリングクラッシュ修正 設計ドキュメント

## TL;DR

`frontend/app.json`の`newArchEnabled`を`true`から`false`に変更し、React NativeのNew Architecture（Fabric/TurboModules）を無効化することで、`@jitsi/react-native-sdk`とNew Architectureの非互換（[requirements.md](requirements.md)参照）によるクラッシュを解消する。調査の結果、New Architecture専用の`react-native-reanimated`/`react-native-worklets`は実アプリ（`app/`配下）では未使用（未参照のテンプレート由来コンポーネントのみが使用）と判明したため、無効化の妨げにならないよう合わせて削除する。ネイティブプロジェクトを`expo prebuild --clean`で再生成し、dev clientを再ビルドして動作確認する。

## Non-Goals

[requirements.md](requirements.md)のNon-Goalsを引き継ぐ。加えて設計上、以下は対象外とする。

- `@jitsi/react-native-sdk`のバージョン変更・fork・パッチ適用（アップストリームで解決策が確認できていないため）。
- New Architectureを維持したまま原因を特定・回避する対応（後述の通り、アップストリームで既知の未解決問題であり、このリポジトリ側だけでの回避は現実的ではないと判断）。
- `react-native-screens`, `react-native-gesture-handler`等、Old Architectureでも動作する他のライブラリ自体の設定変更（変更不要）。
- 将来的なアニメーション機能の追加方法の検討（今回削除する`react-native-reanimated`の代替が必要になった場合の対応は本タスクのスコープ外）。

## 検討した代替案

### 案A: New Architectureを無効化する（採用）

`app.json`の`newArchEnabled`を`false`にし、Old Architecture（Paper）でビルドし直す。

- 長所: アプリ側の設定変更のみで完結し、`@jitsi/react-native-sdk`のコードには一切手を入れない。requirements.mdで確認した複数のアップストリーム課題（New Architecture有効時のクラッシュ報告）に直接対応する。
- 短所: 将来的にNew Architectureへの移行が必須になった場合（React Native側でOld Architectureが廃止される等）、Jitsi SDK側の対応を待つか、ライブラリの入れ替えが必要になる。

### 案B: `@jitsi/react-native-sdk`のバージョンを変更する

New Architectureと互換性のあるバージョンを探して固定する。

- 却下理由: requirements.mdで調査した範囲では、New Architectureに対応済みであることを明言しているバージョンはアップストリームで確認できなかった（複数バージョンで同種の非互換が継続的に報告されている）。バージョン変更だけで直るという裏付けがなく、検証コストに見合わない。

### 案C: 原因コンポーネントを特定し、アプリ側でラップ/差し替えて回避する

クラッシュしているコンポーネントを特定し、代替実装やエラーバウンダリで握りつぶす。

- 却下理由: 原因がJitsi SDK内部（`@jitsi/react-native-sdk`のnode_modules配下）にあるため、アプリ側から個別のコンポーネントを差し替えることは事実上不可能（パッケージの改変が必要になり、Non-Goalsの「SDK自体のパッチ適用」に抵触する）。

## 設計

1. `react-native-reanimated`/`react-native-worklets`（New Architecture専用）を`package.json`から削除する（`yarn remove`）。使用箇所は`app/`から未参照の`components/hello-wave.tsx`・`components/parallax-scroll-view.tsx`・`sample/`配下のみであり、実アプリの挙動に影響しない。`react-native-worklets-core`は`@jitsi/react-native-sdk`自体の依存（Old Architectureでも動作）のため維持する。同様に、Old Architectureではcodegenインターフェース（`RNCViewPagerManagerDelegate`等）が生成されずビルド不能になる`react-native-pager-view`も、コードベース内で未使用（未参照の直接依存）と確認できたため削除する。
2. `frontend/app.json`の`expo.newArchEnabled`を`false`に変更する。
3. ネイティブプロジェクトはNew Architecture有効な状態で生成済みのため、`npx expo prebuild --clean`で`frontend/android/`（および`frontend/ios/`が存在する場合はそちらも）を再生成する。`frontend/.gitignore`で`/android`・`/ios`は除外されている（生成物であり都度再生成される前提）ため、削除・再生成してよい。
4. `npx expo run:android`（Windows環境では[frontend/scripts/run-android.ps1](../../../frontend/scripts/run-android.ps1)、`npm run android:win`）でdev clientを再ビルド・再インストールし、Metroに接続する。
5. [manuals/video-call-testing.md](../../../manuals/video-call-testing.md)の手順に従い、Home画面の「一人で対話を開始する」ボタンからMeeting画面を開き、LogBoxに`Element type is invalid`のConsole Error/Render Errorが出ないこと、Jitsi Meetの通話UIが表示されることを確認する。

## 横断的関心事

- **セキュリティ・プライバシー**: 影響なし。認可境界やデータの扱いに変更はない。
- **パフォーマンス・スケーラビリティ**: `react-native-reanimated`は未使用のため削除する（性能への影響なし）。パフォーマンス計測は本タスクのスコープ外（要件のNon-Goalsの通り）。
- **オブザーバビリティ**: 影響なし。本アプリに自動収集のログ・メトリクス基盤は導入されていない（[docs/backend.md](../../../docs/backend.md)/[docs/frontend.md](../../../docs/frontend.md)の通り）。手動での動作確認のみで足りると判断。
- **テスト戦略**: [manuals/video-call-testing.md](../../../manuals/video-call-testing.md)に基づく手動確認のみ。自動テストの追加はrequirements.mdのNon-Goals。
- **ロールアウト計画**: ローカル開発環境の設定変更であり、段階的リリースやマイグレーションは不要。問題が起きた場合は`newArchEnabled`を`true`に戻し、必要であれば`react-native-reanimated`/`react-native-worklets`を再インストールした上で`expo prebuild --clean`し直せばロールバックできる。

## 既存アーキテクチャとの整合性

[docs/frontend.md](../../../docs/frontend.md)には現時点でNew Architectureに関する記載がない。今回`newArchEnabled: false`に変更する（意図的な逸脱ではなく、`@jitsi/react-native-sdk`との非互換を踏まえた明示的な選択）ため、実装時に[docs/frontend.md](../../../docs/frontend.md)へその旨を追記し、今後別の開発者が誤って`true`に戻さないようにする。
