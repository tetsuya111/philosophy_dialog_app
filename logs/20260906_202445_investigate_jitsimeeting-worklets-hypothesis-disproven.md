# 作業ログ: JitsiMeeting Element type is invalid調査 - worklets-core仮説の否定と診断ログ追加

## 何を行ったか

- `.kiro/specs/fix-jitsimeeting-element-invalid/tasks.md`を新規作成した。
- ユーザーが`babel.config.js`の`react-native-worklets-core/plugin`を一時的にコメントアウトして再現確認した結果を確認 → `Element type is invalid ...got: number`は同じ箇所（`components/Meeting.tsx:35`の`<JitsiMeeting`）で引き続き発生。worklets-core起因の仮説を否定した。
- `components/Meeting.tsx`に`typeof JitsiMeeting`・値そのものを出力する診断用`console.log`を一時的に追加した。
- `.kiro/specs/fix-jitsimeeting-element-invalid/requirements.md`に上記結果を反映した。

## なぜ行ったか

worklets-coreのBabel変換が`<JitsiMeeting>`要素の破損原因である可能性を最有力仮説として検証したが、プラグインを無効化しても同じエラーが再現したため否定された。次に、`JitsiMeeting`という値自体がインポート時点でどうなっているかを直接確認するため、診断ログを仕込んだ。この情報が得られれば、モジュール解決の異常（Metroのモジュールid漏れ等）か、他の原因かを確定できる。

## 残作業

[CLAUDE.md](../CLAUDE.md)の方針により、ビルド・動作確認とターミナルログの確認はユーザーに依頼する（`.kiro/specs/fix-jitsimeeting-element-invalid/tasks.md`タスク3）。
