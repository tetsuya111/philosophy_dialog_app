# 作業ログ: SDK location not foundエラー再発の原因調査とlocal.properties応急対応

## 何を行ったか

- `frontend/android/local.properties`に`sdk.dir`（Android SDKの実在パス）を直接作成した。
- `.kiro/specs/fix-android-sdk-location-error/requirements.md`のオープンクエスチョンと`tasks.md`に、再発原因と対応内容を反映した。

## なぜ行ったか

前回`ANDROID_HOME`をユーザー環境変数として永続設定したにもかかわらず、ユーザーが新しいターミナルで`npm run android:win`を実行したところ、同一の`SDK location not found`エラーが再発した。

原因を調査した結果、Windowsのユーザー環境変数への変更は**既に起動済みのプロセスツリーには反映されない**ことが分かった。特にVS Codeの統合ターミナルは、VS Code本体プロセスの起動時点の環境変数を引き継ぐため、ターミナルタブを新しく開いただけでは`ANDROID_HOME`の変更が反映されず、VS Code自体の再起動が必要になる。ユーザーが試した「新しいターミナル」がこの条件を満たしていなかったと推測される。

この問題は新規のバグではなく、直前に対応した`.kiro/specs/fix-android-sdk-location-error/`と同一のエラーの再発であるため、重複したrequirements.mdを新規作成せず、既存specの内容を更新する形で対応した（[CLAUDE.md](../CLAUDE.md)の「同じ内容を複数のドキュメントに重複して書かない」方針に従った）。

ターミナル/IDEの再起動を待たずに即座に効く対策として、Gradleがビルドのたびに読む`frontend/android/local.properties`に`sdk.dir`を直接書き込む応急対応を追加した。ただし、このファイルは`.gitignore`対象かつ`expo prebuild --clean`のたびに消える生成物であるため、恒久対応ではない点を`requirements.md`に明記した。

## 残作業

ユーザーに(a) 現在のターミナルのまま`local.properties`による応急対応で解決するか、(b) VS Code再起動後に`ANDROID_HOME`単体でも解決するかを確認してもらう（[.kiro/specs/fix-android-sdk-location-error/tasks.md](../.kiro/specs/fix-android-sdk-location-error/tasks.md)タスク7）。
