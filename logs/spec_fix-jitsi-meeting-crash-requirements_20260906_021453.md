# Jitsi Meetingクラッシュ修正のrequirements.md作成

## 何を

`.kiro/specs/fix-jitsi-meeting-crash/requirements.md`を新規作成。ユーザーがAndroid実機/エミュレータで報告した「Element type is invalid: expected a string...but got: number」というConsole Error/Render Error（Meeting画面を開いた際にJitsi SDK内部`BaseApp.tsx`のcomponentDidCatchで捕捉されるクラッシュ）に対処する修正の要件定義書を作成した。WebSearch/WebFetchでjitsi/jitsi-meetのGitHub issue（#17194, #16443, #16849, #14912）を調査し、`@jitsi/react-native-sdk`とReact NativeのNew Architecture（Fabric/TurboModules、本プロジェクトの`app.json`で`newArchEnabled: true`）の非互換がアップストリームで複数報告されていることを確認し、背景・参考情報として記載した。断定はできないため「オープンクエスチョン」として原因特定タスクを明記している。

## なぜ

ユーザーからの依頼。ビデオ通話は本アプリの中核機能であり、現状クラッシュして使えない状態のため、要件定義（What: クラッシュせず通話UIが表示されること）を設計・修正に先立って明文化した。
