# タスクリスト

[requirements.md](requirements.md)を元に、実行可能な単位に分解したもの。上から順に実施する（design.mdは作成せず、要件定義から直接タスク化する方針とした）。

## 方針

調査の結果、`ANDROID_HOME`/`ANDROID_SDK_ROOT`はこのマシンの現在のユーザーアカウントに一度も永続設定されたことがない（レジストリのユーザー環境変数に存在しない）ことを確認した。Gradle自身が案内する2つの標準的な解決策（`ANDROID_HOME`環境変数 / `local.properties`の`sdk.dir`）のうち、`local.properties`は`expo prebuild`のたびに再生成され消える生成物であるため、恒久対応としては**`ANDROID_HOME`をユーザー環境変数として永続設定する**方式を採用する。これによりAndroid Studio等、他のAndroidツールとも共通の標準的な仕組みに乗る。`local.properties`は、`ANDROID_HOME`設定後に`expo prebuild`を実行し直せばExpo CLIが自動生成することを検証で確認する。

- [x] 1. ユーザー環境変数`ANDROID_HOME`を`%LOCALAPPDATA%\Android\Sdk`（検出済みのSDK実在パス）に永続設定する（`[Environment]::SetEnvironmentVariable`で設定。レジストリのユーザー環境変数に反映済み）。
- [x] 2. [docs/frontend.md](../../../docs/frontend.md)のセットアップ手順に、Android実機/エミュレータ向けビルド（`npm run android:win`等）には`ANDROID_HOME`環境変数の設定が前提であることを追記する。
- [x] 3. `frontend`ディレクトリで`npx expo prebuild --clean`を実行し、`frontend/android/local.properties`が`sdk.dir`付きで自動生成されるか確認する（`ANDROID_HOME`が認識される状態で実行）。→ **結果: 自動生成されなかった**（このプロジェクト/expoバージョンの`prebuild`は`local.properties`を生成しない仕様と判明）。requirements.mdのオープンクエスチョンを参照。
- [x] 4. ~~生成された`frontend/android/local.properties`の内容を確認~~ → タスク3の結果、`local.properties`自体が生成されないため対象外。Gradleは`local.properties`の`sdk.dir`ではなく`ANDROID_HOME`環境変数のみで場所を解決する前提に変更。
- [x] 5. ユーザーが新しいターミナルで`npm run android:win`を実行 → **同じ`SDK location not found`エラーが再発**。原因調査の結果、VS Code統合ターミナルは新しいタブを開いただけでは`ANDROID_HOME`永続設定を引き継がない（VS Code本体の再起動が必要）と判明。requirements.mdに反映済み。
- [x] 6. 応急対応として`frontend/android/local.properties`に`sdk.dir`を直接作成した（プロセスの環境変数状態に依存せず即座に有効）。**注意**: `.gitignore`対象かつ`expo prebuild --clean`のたびに消えるため、prebuildをやり直した場合は再作成が必要。
- [ ] 7. ユーザーに、(a) 現在のターミナルのまま`npm run android:win`を再実行して`local.properties`による応急対応で`SDK location not found`が解消するか、(b) VS Codeを再起動した上で`ANDROID_HOME`永続設定単体でも解決するか、のいずれかを確認してもらう（[CLAUDE.md](../../../CLAUDE.md)の方針により手動実行を促す）。
- [ ] 8. 確認結果を`requirements.md`の「オープンクエスチョン」および本ファイルに反映する。
- [ ] 9. 作業ログを`logs/`に記録する。
