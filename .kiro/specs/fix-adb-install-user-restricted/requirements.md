# 実機へのdev clientインストール失敗（INSTALL_FAILED_USER_RESTRICTED）修正 要件定義書

## 背景・課題（Working Backwards）

[.kiro/specs/fix-jitsi-config-network-error/](../fix-jitsi-config-network-error/)の切り分け（エミュレータ固有のネットワーク問題かどうかを実機で確認する）のため、実機（Xiaomi Redmi Note 9S、Android 12、MIUI）に対して`npx expo run:android`でdev clientをインストールしようとしたところ、以下のエラーでインストールに失敗した。

```
Error: adb.exe: failed to install ...\app-debug.apk: Failure [INSTALL_FAILED_USER_RESTRICTED: Install canceled by user]
```

`adb devices`では端末は認識されており（USBデバッグ自体は有効化済み）、`adb -s <serial> install`コマンドがADB経由でのインストール自体を拒否されている状態。

### 判明している事実

- 対象端末: Xiaomi Redmi Note 9S（`ro.product.manufacturer=Xiaomi`、Android 12、MIUI）。
- `INSTALL_FAILED_USER_RESTRICTED`は、Android標準のエラーコードで「ユーザーによってインストールがキャンセルされた」ことを示す。実機の画面上でインストール許可の確認ダイアログが表示され、それが承認されなかった（またはタイムアウトした）場合に発生する。
- **MIUI（Xiaomi端末）固有の既知の制限**: MIUIは通常の「USBデバッグ」に加えて、開発者向けオプション内に**「USBデバッグ（セキュリティ設定）」**という別のトグルがあり、これを有効にしないとADB経由でのアプリインストール（`adb install`）がブロックされ、まさに本エラー（`INSTALL_FAILED_USER_RESTRICTED`）が発生することが広く知られている。このトグルはXiaomiアカウントへのログインが必要な場合がある。

## スコープ / Non-Goals

**スコープ:**

- 実機（Xiaomi Redmi Note 9S、MIUI）に対して`npx expo run:android` / `npm run android:win`でdev clientのインストールが成功する状態にすること。

**Non-Goals（今回は対応しない）:**

- MIUI以外のメーカー（Samsung, Google Pixel等）での同種の制限の網羅的な調査（今回発生した端末のみを対象とする）。
- [.kiro/specs/fix-jitsi-config-network-error/](../fix-jitsi-config-network-error/)の本題（Jitsi接続の不安定さがエミュレータ固有かどうか）そのものの検証（本specはそのための前提条件＝実機インストールの障害を解消するのが目的）。
- Wi-Fi経由のワイヤレスデバッグ（`adb pair`/`adb connect`）への切り替え（USB接続でのインストールを前提とする）。

## 成功指標

- 実機に対して`npm run android:win`を実行した際、`INSTALL_FAILED_USER_RESTRICTED`エラーが発生せず、dev clientのインストールが完了すること。
- インストール後、実機上でアプリが起動しMetroに接続できること。

## ユーザーストーリー・受け入れ基準

**ユーザーストーリー**: As a 開発者, I want 実機にdev clientをUSB経由でインストールしたい, so that Jitsi通話機能をエミュレータだけでなく実機でも検証できる。

- WHEN 実機（Xiaomi/MIUI端末）に対して`adb install`（`npx expo run:android`経由を含む）を実行したとき THE SYSTEM SHALL `INSTALL_FAILED_USER_RESTRICTED`エラーを発生させることなくAPKをインストールする。
- IF MIUIの「USBデバッグ（セキュリティ設定）」が無効になっていることが原因の場合 THEN THE SYSTEM SHALL （ユーザー操作により）これを有効化することでインストールが成功することを確認する。
- IF 「USBデバッグ（セキュリティ設定）」を有効化してもなお失敗する場合 THEN THE SYSTEM SHALL 別の原因（インストール確認ダイアログの見落とし・画面ロック中のタイムアウト等）を切り分ける。

## 非機能要件

- 本対応は端末側の設定変更のみで完結させ、プロジェクトのコード・ビルド設定（`app.json`、Gradle設定等）は変更しない（端末固有の制限であり、リポジトリ側の問題ではないため）。

## オープンクエスチョン（ユーザーによる実機操作で確定させること）

- ~~MIUIの「USBデバッグ（セキュリティ設定）」を有効化すれば直るか~~ → **有効化したが解消せず**。同一の`INSTALL_FAILED_USER_RESTRICTED`が再発した。MIUI側の制限は複数レイヤーあるため、他の要因を切り分ける必要がある。

### 追加で疑われる原因（MIUI特有）

1. **「MIUI最適化（MIUI optimization）」がONのまま**: 開発者向けオプション内の「MIUI最適化を有効にする」をOFFにすることで、ADB経由のインストール制限が解除される事例が多数報告されている。まず試すべき対策。
2. **インストール確認ダイアログを見逃している**: 画面ロック中・他アプリ操作中にインストールを実行すると、実機側に表示される「USB経由でのインストールを許可しますか」的な確認ダイアログがタイムアウトし、自動的にキャンセル扱いになる。インストール実行中は画面をロック解除した状態で手元に置き、ダイアログが出たら即座に許可する必要がある。
3. **Xiaomiアカウントが未サインイン、またはサインイン済みだが端末がオフライン**: 「USBデバッグ（セキュリティ設定）」はXiaomiアカウントでのオンライン検証を伴う場合があり、Wi-Fi接続なしでは設定が実質的に反映されないことがある。
4. **「不明なアプリのインストール」権限が特定のインストーラー（ADB/シェル経由）に対して個別にブロックされている**: MIUIの「セキュリティ」アプリ内で、アプリごとのインストール許可設定を確認する。

### 代替手段（上記で解決しない場合）

- `adb install`を使わず、`app-debug.apk`を端末にファイル転送し、端末のファイルマネージャーから手動でタップしてインストールする（ADB経由の制限を回避できる、実務上よく使われる回避策）。

次の一手として、まず「1. MIUI最適化のOFF」と「2. 画面ロック解除・ダイアログ確認」を試してもらう。

### 追加調査（`dumpsys`によるOS標準層の切り分け）

`adb shell dumpsys user`・`adb shell dumpsys device_policy`で確認したところ、以下が判明した。

- ユーザーは`所有者`（Owner、User 0、isPrimary=true）のみで、MIUIの「第二空間」やゲストユーザーには入っていない。
- User 0の`Restrictions` / `Device policy global restrictions` / `Device policy local restrictions` / `Effective restrictions`はいずれも**空**（Android標準の`UserManager`による`DISALLOW_INSTALL_APPS`等の制限は設定されていない）。
- 有効なDevice Admin（MDM等の管理者アプリ）も登録されていない。

**結論**: Android標準のOS層（`UserManager`/`DevicePolicyManager`）には制限がなく、`INSTALL_FAILED_USER_RESTRICTED`はMIUI独自のセキュリティレイヤー（「セキュリティ」アプリのインストール許可管理等、ADBから introspect できない部分）由来と判断する。トグルを推測で探し続けるより、**ADBのインストール経路を使わない代替手段**に切り替えることを推奨する。

### 推奨する代替手段（ADBインストールを回避する）

1. `adb push`でAPKファイルを端末のダウンロードフォルダに転送する。
2. 端末の「ファイル」アプリ（文件管理/Files）からダウンロードフォルダを開き、APKファイルをタップしてインストールする（初回は「この提供元からのアプリのインストールを許可」の確認が出る場合があるため許可する）。
3. インストール後、アプリを手動で起動し、Metro（PC側で起動中の開発サーバー）に接続できることを確認する。

この方法はADB経由のインストール（`adb install`）とは別の、Android標準の「ファイルからのインストール」経路を使うため、MIUI独自のADB向け制限を回避できる可能性が高い。

## 結果（解決）

上記の代替手段（`adb push`＋ファイルマネージャーからの手動インストール）を実施したところ、インストールに成功し、アプリが実機で起動することを確認した。

**結論**: `INSTALL_FAILED_USER_RESTRICTED`はMIUI独自のADB向けセキュリティ制限が原因（詳細な条件は特定できていないが、Android標準の`UserManager`/`DevicePolicyManager`層の制限ではないことは確認済み）。`adb install`経由でのインストールを回避することで解決した。今後この端末に新しいビルドを試す際は、同じ手順（`adb push`→端末のファイルマネージャーからインストール）を使うこと。
