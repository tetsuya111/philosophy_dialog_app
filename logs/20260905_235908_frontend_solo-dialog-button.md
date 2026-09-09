# 「一人で対話を開始する」ボタンの実装

## 何を

- `frontend/app/(tabs)/index.tsx` に「一人で対話を開始する」ボタンを追加。押下すると`solo-<timestamp>-<random>`形式のルーム名を生成し、`/meeting`ルートに遷移する。
- `frontend/app/meeting.tsx` を新規作成。`useLocalSearchParams`で`room`を受け取り`Meeting`コンポーネントに渡すexpo-routerの正式な画面として実装。
- `frontend/app/_layout.tsx` のルートStackに`meeting`画面を登録（`headerShown: false`、`fullScreenModal`）。
- `frontend/components/Meeting.tsx`/`Meeting.web.tsx` のprops契約を、react-navigation前提の`route.params.room`からexpo-router前提の`room: string`直接受け取りに変更。あわせて`onReadyToClose`のナビゲーションを`useNavigation().navigate('Home')`から`useRouter().back()`に変更。
- 上記のprops変更に伴い型エラーとなった`frontend/app/App.tsx`（react-navigation Stackで`Home`→`Meeting`を配線していた未使用の遺物、expo-routerのルーティングからは到達不可能と既に判明していたもの）と、それが唯一の呼び出し元だった`frontend/components/Home.tsx`を削除。

## なぜ

ユーザーからの依頼で、マッチングを介さず一人でも対話（ビデオ通話）画面に入れるボタンを実装するため。実装にあたり、`manuals/video-call-testing.md`作成時に判明していた「Meeting画面がexpo-routerの実ルーティングから到達不可能」という既知の課題を、正式なexpo-routerの画面（`app/meeting.tsx`）を追加する形で解消した。これにより`app/App.tsx`（react-navigation前提の未使用コード）がpropsの変更で型エラーになったため、到達不可能な死んだコードとして削除した。
