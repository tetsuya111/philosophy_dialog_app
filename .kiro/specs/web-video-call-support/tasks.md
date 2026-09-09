# タスクリスト

[design.md](design.md)の「設計」セクションを実行可能な単位に分解したもの。上から順に実施する。

- [x] 1. `frontend/components/Meeting.web.tsx`に、`https://meet.jit.si/external_api.js`を動的に読み込むヘルパー処理を実装する（`window.JitsiMeetExternalAPI`が既に存在する場合は再読み込みしない）。
- [x] 2. `Meeting.web.tsx`本体を実装する。`useRef`で確保した`View`のDOMノードを`parentNode`として`JitsiMeetExternalAPI`をインスタンス化し、`roomName`に`room` propを渡す。
- [x] 3. `readyToClose`イベントに`expo-router`の`useRouter().back()`を紐付ける（ネイティブ版`Meeting.tsx`の`onReadyToClose`と同等の挙動）。
- [x] 4. コンポーネントのアンマウント時（`useEffect`のクリーンアップ）に`api.dispose()`を呼び出す。
- [x] 5. スクリプト読み込み中のローディング表示、読み込み失敗時のエラー表示を実装する（現状の「モバイルアプリでのみ」という誤った文言のまま失敗させない）。
- [x] 6. [docs/frontend.md](../../../docs/frontend.md)のアーキテクチャ節に、Web版は`external_api.js`を使う旨を追記する。
- [x] 7. [manuals/video-call-testing.md](../../../manuals/video-call-testing.md)に、Web版の確認手順（`npm run web`で起動しHome画面から通話を開始する、別のブラウザタブ/別端末から同じルーム名の`https://meet.jit.si/<room>`にアクセスして映像・音声が双方向に繋がることを確認する）を追記する。
- [x] 8. `npm run web`で実際に動作確認する。Home画面の「一人で対話を開始する」ボタンから遷移し、Jitsi Meetの通話UI（カメラ映像・マイク入力）が表示されることを確認する（[requirements.md](requirements.md)の成功指標1点目）。
- [x] 9. 別のブラウザタブ/別端末から同じルーム名でアクセスし、Web版から見た映像・音声が相互に届くことを確認する（[requirements.md](requirements.md)の成功指標2点目）。
- [x] 10. 作業ログを`logs/`に記録する。
