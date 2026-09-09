# Android開発ビルドの「SDK location not found」エラー修正 要件定義書

## 背景・課題（Working Backwards）

Windows環境で`frontend`ディレクトリから`npm run android:win`（[frontend/scripts/run-android.ps1](../../../frontend/scripts/run-android.ps1)経由で`npx expo run:android`を実行）を行うと、Gradleビルドが以下のエラーで失敗し、Android実機/エミュレータへのdev clientインストールができない。

```
FAILURE: Build failed with an exception.

* What went wrong:
Could not determine the dependencies of task ':app:compileDebugJavaWithJavac'.
> SDK location not found. Define a valid SDK location with an ANDROID_HOME environment variable or by setting the sdk.dir path in your project's local properties file at 'C:\Users\USER\projects\philosophy_dialog_event_group\philosophy_dialog_app_claude\frontend\android\local.properties'.

BUILD FAILED in 4s
28 actionable tasks: 28 up-to-date
```

「28 actionable tasks: 28 up-to-date」という表示の通り、実際には1つもコンパイルタスクが実行されておらず、Gradleの設定（configuration）段階でAndroid SDKの場所を解決できずに即座に失敗している。

調査の結果、以下が判明している。

- `frontend/android/local.properties`（Gradleが`sdk.dir`を読み取るファイル）は存在しない。
- `ANDROID_HOME`・`ANDROID_SDK_ROOT`環境変数は、通常のPowerShellターミナル・Git Bashターミナルのいずれにも設定されていない（ユーザーのシェルプロファイルに永続化されていない）。
- 一方でAndroid SDK自体は`%LOCALAPPDATA%\Android\Sdk`（デフォルトの場所）に実在する。
- [frontend/scripts/run-android.ps1](../../../frontend/scripts/run-android.ps1)は、`adb.exe`のパス解決にのみ`ANDROID_HOME`→`ANDROID_SDK_ROOT`→`%LOCALAPPDATA%\Android\Sdk`のフォールバックを行っているが、これは`adb reverse`等スクリプト自身の処理のためだけであり、後続で実行される`npx expo run:android`（Gradle）にはこの情報が渡っていない。
- `npx expo prebuild`（`android/`ディレクトリの再生成）を行った際も、`local.properties`は自動生成されなかった。

このため、`ANDROID_HOME`が事前に設定されていない開発者・端末では、[.kiro/specs/fix-jitsi-meeting-crash/](../fix-jitsi-meeting-crash/)で行っているAndroidビルド確認作業（`expo prebuild --clean` → `npx expo run:android`）が毎回このエラーで止まってしまう。

## スコープ / Non-Goals

**スコープ:**

- `frontend`ディレクトリでAndroid向けdev clientビルド（`npx expo run:android` / `npm run android:win` / [frontend/scripts/run-android.ps1](../../../frontend/scripts/run-android.ps1)）を実行した際に、Android SDKの場所を解決できず`SDK location not found`で失敗する問題の解消。
- Windows環境（PowerShell）における恒久的な解決（`ANDROID_HOME`が未設定のセッションでも、毎回手動で環境変数を設定しなくてもビルドが通ること）。

**Non-Goals（今回は対応しない）:**

- Android SDK自体のインストール・セットアップ手順の整備（SDKが存在すること自体は確認済みであり、その場所をビルドに伝える仕組みが今回の対象）。
- macOS/Linux環境での同種の問題（今回はWindows環境での発生のみ確認済み。スコープ外）。
- CI環境での自動ビルド設定（現時点でCIパイプラインは未導入。導入時は別途検討）。
- [.kiro/specs/fix-jitsi-meeting-crash/](../fix-jitsi-meeting-crash/)のNew Architecture無効化に伴う他の修正内容そのもの（本件はそのタスク実行中に発生した、独立した環境起因の問題として扱う）。

## 成功指標

新機能ではなく開発環境起因の不具合修正のため、以下を満たすことをもって成功とする。

- `ANDROID_HOME`・`ANDROID_SDK_ROOT`のいずれも設定していない新規のPowerShellターミナルから`npm run android:win`を実行した場合に、`SDK location not found`エラーで停止しないこと（SDKの場所解決自体は成功し、後続のコンパイル・インストール処理に進むこと）。
- [docs/frontend.md](../../../docs/frontend.md)のセットアップ手順に従うだけで、Android SDKのパスをビルドに認識させるための追加手順が明確であること（もしくは自動化されていること）。

## ユーザーストーリー・受け入れ基準

**ユーザーストーリー**: As a フロントエンド開発者, I want 新しいターミナルセッションでもAndroidビルドがSDKの場所を自動的に認識してほしい, so that ビルドのたびに`ANDROID_HOME`を手動設定しなくても`npm run android:win`が実行できる。

- WHEN `ANDROID_HOME`・`ANDROID_SDK_ROOT`環境変数が設定されていないPowerShellセッションから`npm run android:win`を実行したとき THE SYSTEM SHALL Android SDKの場所を解決し、`SDK location not found`エラーを発生させることなくGradleのコンパイルタスクを実行する。
- IF `frontend/android/local.properties`が存在しない、または`sdk.dir`が未設定の場合 THEN THE SYSTEM SHALL デフォルトのSDKインストール先（`%LOCALAPPDATA%\Android\Sdk`）を検出して`sdk.dir`を補完する、もしくは`ANDROID_HOME`を解決してGradleに渡す。
- IF デフォルトの場所にもAndroid SDKが見つからない場合 THEN THE SYSTEM SHALL `SDK location not found`のGradle標準エラーに加えて、`ANDROID_HOME`の設定方法（[docs/frontend.md](../../../docs/frontend.md)参照）を案内するメッセージを表示する。

**ユーザーストーリー**: As a 開発者, I want この問題が`expo prebuild`のたびに再発しないでほしい, so that `android/`ディレクトリを再生成するたびに同じエラーに遭遇して調査し直す手間をなくしたい。

- WHEN `npx expo prebuild`（`--clean`含む）で`frontend/android/`が再生成されたとき THE SYSTEM SHALL 再生成後も`ANDROID_HOME`未設定のセッションからビルドが実行できる状態を維持する（`local.properties`は`.gitignore`対象の生成物であるため、prebuildのたびに失われることを前提とした対策にする）。

## 非機能要件

- 対応方法は、Gradle・Android SDKの標準的な仕組み（`local.properties`の`sdk.dir`、環境変数`ANDROID_HOME`）に沿ったものとし、独自の回避策（ビルドスクリプトでのハードコードされた絶対パス等、他の開発者のマシン構成で通用しない方法）を避ける。
- ユーザー個別の環境（Android SDKのインストール先）に依存する設定は、リポジトリにコミットされるファイルに直接書き込まない（`local.properties`が`.gitignore`対象になっている現状の方針を維持する）。

## オープンクエスチョン（[tasks.md](tasks.md)での検証結果）

- **一次対応**: `ANDROID_HOME`をユーザー環境変数として永続設定した（`[Environment]::SetEnvironmentVariable("ANDROID_HOME", ..., "User")`）。`local.properties`との併用は不要と判断した。
- **判明した事実（1）**: `ANDROID_HOME`をこのセッションに設定した状態で`npx expo prebuild --clean`を実行しても、`frontend/android/local.properties`は生成されなかった。このプロジェクトで使用しているExpo CLIのバージョンでは、`prebuild`が`local.properties`を自動生成しない（もしくは特定条件でのみ生成する）ことが確認された。
- **判明した事実（2・再発の原因）**: `ANDROID_HOME`永続設定後も、同一の`SDK location not found`エラーが再発した。原因は、Windowsのユーザー環境変数の変更が**既に起動済みのプロセスツリーには反映されない**ため。特にVS Codeの統合ターミナルは、VS Code本体プロセス起動時点の環境変数を引き継ぐため、ターミナルタブを新しく開くだけでは不十分で、**VS Code自体の再起動（プロセスの再起動）が必要**。ユーザーが試した「新しいターミナル」がこの条件を満たしていなかった可能性が高い。
- **追加対応**: ターミナル/IDEの再起動に依存せず即座に効く対策として、`frontend/android/local.properties`に`sdk.dir`を直接書き込んだ（Gradleはビルドのたびにこのファイルを読むため、プロセスの環境変数状態に依存しない）。ただし`local.properties`は`.gitignore`対象かつ`expo prebuild --clean`のたびに消える生成物のため、**`prebuild`をやり直すたびに再作成が必要**という制約が残る（[tasks.md](tasks.md)参照）。
- 残課題: 恒久的には`ANDROID_HOME`永続設定が有効になる（VS Code再起動後）ことを確認する。`prebuild`のたびに`local.properties`の再作成が必要な点をどう省力化するか（例: `expo-build-properties`やpostinstallスクリプトでの自動化）は、今後の課題として残す（今回はスコープ外・応急対応のみ）。
