# 作業ログ: fix-jitsi-meeting-crashの根本原因の再調査（依存バージョン不整合）

## 何を行ったか

- 実機で「Element type is invalid: ...got: number」の元々のクラッシュが、New Architecture無効化後も再現することを確認した。
- `@jitsi/react-native-sdk`の`peerDependencies`と、プロジェクトの実際のインストールバージョンを全パッケージ照合し、広範な不整合（`react-native`本体が`~0.77.0`要求に対し実際は`0.81.5`、他多数のパッケージがメジャーバージョン違い、独自フォーク4パッケージが通常npm版で代替されている）を発見した。
- npmレジストリ・Jitsiの変更履歴（CHANGELOG-MOBILE-SDKS.md）をWeb調査し、`@jitsi/react-native-sdk`のバージョン別react-native対応状況を確認した（11.x/12.x→Old Architecture・RN 0.77〜0.79系、13.x→New Architecture必須・RN 0.85.2）。
- `.kiro/specs/fix-jitsi-meeting-crash/requirements.md`にこれらの調査結果を反映した。

## なぜ行ったか

`fix-jitsi-config-network-error`のBabel設定修正により会議接続・マイク/カメラ権限まで到達できるようになったため、`fix-jitsi-meeting-crash`本来のクラッシュを再確認したところ、New Architecture無効化では直っていないことが判明した。これはdesign.mdの前提（New Architecture非互換が原因）を覆す重要な発見であり、真の原因を特定するため依存関係のバージョンを網羅的に調査した。

調査の結果、プロジェクトの`react-native`（`0.81.5`）が、Jitsi SDKのどのメジャーバージョンの対応範囲にも合致しない「谷間」にあることが分かった（11.x/12.x系は0.81より古いバージョンまで、13.x系は0.81より新しいバージョン・New Architecture必須）。この状態でパッケージ単位の微調整だけで根本解決するかは不透明なため、方向性（現状のRN/Expoバージョンを維持して個別パッケージを合わせるか、Jitsi 13.x系・RN/Expoの大規模アップグレードに踏み切るか）をユーザーに確認する必要があると判断した。
