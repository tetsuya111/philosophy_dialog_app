# 作業ログ: Android SDK location not foundエラー修正の要件定義作成

## 何を行ったか

`.kiro/specs/fix-android-sdk-location-error/requirements.md`を新規作成した。

## なぜ行ったか

[.kiro/specs/fix-jitsi-meeting-crash/](../.kiro/specs/fix-jitsi-meeting-crash/)の対応（New Architecture無効化の動作確認）作業中に、`npm run android:win`実行時のGradleビルドが以下のエラーで失敗する事象が発生したため。

```
* What went wrong:
Could not determine the dependencies of task ':app:compileDebugJavaWithJavac'.
> SDK location not found. Define a valid SDK location with an ANDROID_HOME environment variable or by setting the sdk.dir path in your project's local properties file at '...\frontend\android\local.properties'.
```

調査により、`frontend/android/local.properties`が存在せず、`ANDROID_HOME`/`ANDROID_SDK_ROOT`環境変数も通常のターミナルセッションに設定されていないことが原因と判明した（Android SDK自体は`%LOCALAPPDATA%\Android\Sdk`に実在する）。[frontend/scripts/run-android.ps1](../frontend/scripts/run-android.ps1)は`adb.exe`のパス解決のみ行っており、後続のGradleビルドにはSDKの場所が伝わっていなかった。

`fix-jitsi-meeting-crash`のバグ内容（New Architecture非互換）とは独立した、開発環境起因の別問題であるため、新規specディレクトリとして要件定義書を作成した。design.md/tasks.mdは未作成（要件定義のみ）。
