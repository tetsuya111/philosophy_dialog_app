# Web版ビデオ通話対応のrequirements.md作成

## 何を

`.kiro/specs/web-video-call-support/requirements.md`を新規作成。ユーザーからの「Android版とWeb版のfrontendを一つのプロジェクトに共存できるか」という質問に対し、Expo（React Native, TypeScript）自体がiOS/Android/Webを単一コードベースで提供する仕組みを既に持ち、`Meeting.tsx`/`Meeting.web.tsx`のプラットフォーム分岐で実際に共存済みであることを確認した上で、「共存」自体は既存事実として要件定義書内に明記した。その上で、実質的な課題は「Web版では`Meeting.web.tsx`が非対応メッセージを表示するだけで実際には通話できない」ことだと解釈し、Web版でも実際にJitsi Meetの通話に参加できるようにする方向の要件を記載した。

## なぜ

ユーザーからの依頼。Web版ビデオ通話が未対応（[.kiro/specs/philosophy-dialog-app/requirements.md](../../.kiro/specs/philosophy-dialog-app/requirements.md)の既知の課題、および`manuals/video-call-testing.md`の前提・制約に記載済み）である点について、対応の方向性を要件として明文化した。解釈が質問の意図とずれている可能性があるため、requirements.md内の「前提の確認」セクションで解釈を明示し、オープンクエスチョンとしてユーザー確認が必要な旨も記載している。
