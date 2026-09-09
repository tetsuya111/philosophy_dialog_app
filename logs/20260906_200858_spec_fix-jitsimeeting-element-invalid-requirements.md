# 作業ログ: JitsiMeeting要素のElement type is invalidの要件定義作成

## 何を行ったか

- `.kiro/specs/fix-jitsimeeting-element-invalid/requirements.md`を新規作成した。
- `node_modules/@jitsi/react-native-sdk/index.tsx`のソースを確認し、`JitsiMeeting`が`forwardRef`で正しくエクスポートされていることを確認した。

## なぜ行ったか

[.kiro/specs/fix-jitsi-nested-navigation-container/](../.kiro/specs/fix-jitsi-nested-navigation-container/)でNavigationContainerの二重ネストを解消した後、[.kiro/specs/fix-jitsi-meeting-crash/](../.kiro/specs/fix-jitsi-meeting-crash/)最初のクラッシュ（`Element type is invalid: ...got: number`）が再発した。ただし今回はスタックトレースが`components/Meeting.tsx:35`の`<JitsiMeeting`タグ自体を直接指しており、以前（`@jitsi/react-native-sdk`内部の`BaseApp.tsx`の`componentDidCatch`で捕捉）より原因箇所を正確に特定できた。

`JitsiMeeting`のエクスポート自体はソースコード上正常なため、Metroのバンドル時に「got: number」（モジュールIDが漏れ出る典型的な症状）が起きている可能性を疑い、[.kiro/specs/fix-worklets-core-missing-babel-plugins/](../.kiro/specs/fix-worklets-core-missing-babel-plugins/)で有効化した`react-native-worklets-core/plugin`のBabel変換が影響している可能性を仮説として記録した。最優先の切り分け方法（babel.config.jsから一時的にworklets-coreプラグインを外してMetro再起動のみで確認する、ネイティブ再ビルド不要）をオープンクエスチョンに整理した。
