# DXナビ（dx-apps）

DX推進室で作成した業務支援ツールを、1つのPWA「DXナビ」にまとめたもの。病棟アプリ（ward-apps）とは別のアプリとして、ホーム画面に追加して使う。

公開URL：https://supernova55md-creator.github.io/dx-apps/

## 収録ツール
- `ks/` 看護師勤務表メーカー（看護）：ヒアリング → ルール → 名簿 → 自動作成
- `nq/` 看護手順 確認テスト（看護）：手順書から作った確認問題と正答率の集計
- `rh/` 自主トレ指導シート（リハ）：運動を選んで配布用シートを印刷
- `tn/` 院内手続きナビ（事務）：用件から書式・提出先・締切を案内
- `qs/` QC発表大会 審査ナビ（TQM・QC）：第26回TQM発表大会の抄録要点・審査票5項目の採点・集計

## 暗号化（DXナビの標準）
- 各ツールの中身は `<slug>/app.enc` に AES-256-GCM（鍵は PBKDF2-SHA256・60万回）で暗号化して置く。リポジトリに平文は置かない
- `<slug>/index.html` はローダー（パスフレーズ入力 → 復号 → 表示）。パスフレーズは DXナビ全体で1つ、salt も共通なので端末は1回入力すれば全ツールが開く
- 「この端末で記憶する」を選ぶと、取り出せない形の鍵（non-extractable CryptoKey）を IndexedDB（`dxnavi`）に保存。入口の「この端末の鍵を消す」で消去
- 平文はどこにも置かない。編集するときは app.enc を復号して取り出す（`tools/decrypt.py`）。パスフレーズはリポジトリ外（Dropbox：Coworks/武蔵野日赤DX推進/dx-apps-src/PASSPHRASE.txt）
- 暗号文は公開されるので、パスフレーズは推測されにくい長い文にする。パスフレーズを変えたら全ツールを暗号化し直し、各端末で入れ直す

## 構成
- `index.html` … 入口（ツール一覧）。新しいツールは一覧に1行追加
- `manifest.webmanifest` … 唯一の manifest（id/start_url/scope は ./、shortcuts に各ツール）
- `tools/` … 暗号化・復号スクリプトとローダーのひな形（秘密情報は含まない）
- `sw.js` … 唯一の service worker。キャッシュ名は `dxnavi-` で始め、ward-apps のキャッシュには触らない
- `<slug>/index.html`（ローダー）・`<slug>/app.enc`（暗号化した中身）とアイコン3つ … 各ツール。ツール側に manifest・service worker は置かない

## 更新するとき
- 編集の流れ：`python3 tools/decrypt.py . <PASSPHRASE.txt> <作業フォルダ>` → 作業フォルダの `<slug>/index.html` を編集 → 作業フォルダに PASSPHRASE.txt を置き `python3 tools/encrypt.py <作業フォルダ> .` → 作業フォルダは削除
- ツールを差し替えたら、`sw.js` の `VERSION` を必ず変える（例 `dxnavi-2026-11-16a` → `b`）
- ツールを追加したら、作業フォルダに `<slug>/index.html` を置いて暗号化し、アイコン3つをリポジトリに置いたうえで、`sw.js` の `APPS`、`manifest.webmanifest` の `shortcuts`、`index.html` の一覧の3か所に足す

## 端末への追加
- iPhone：Safariで入口を開き、共有 →「ホーム画面に追加」。各ツールを開いて追加すれば、ツールごとのアイコンも作れる
- Android：Chromeで入口を開き「アプリをインストール」。アイコン長押しで各ツールに直接入れる

## 注意
- 入力データは端末内（localStorage）のみ。サーバーには送らない。患者を特定できる情報は入力しない
- 公開リポジトリのため、URLを知っていれば誰でも開ける（noindex は設定済み）
- 院内で正式に使う前に、各ツールの内容（看護手順・運動・規程）を担当部署が確認する。手続きナビの規程はデモ用の架空データ
- 勤務表メーカーの「共有」（複数端末での同期）は claude.ai 上の版だけの機能。DXナビ版は端末内保存のみ
