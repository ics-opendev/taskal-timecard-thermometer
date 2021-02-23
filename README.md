taskal-timecard-thermometer
===

TTC(ios) の 体温測定拡張 アプリケーションです。

## OS install

[Raspberry Pi OS Full](https://www.raspberrypi.org/software/)をダウンロード

セットアップアプリをインストールして、
Raspberry Pi OS Fullをインストールする

この[サイト](https://www.itmedia.co.jp/news/articles/2006/05/news031.html)を参考にどうぞ

## ssh setup

初期ユーザ
 loginUser : pi
 password  : raspberry

変更後パスワード : Icsoft123

SSHの有効化
この[サイト](https://qiita.com/tomokin966/items/bc22d09f97ebeb3955d2)を参考にどうぞ

SSHはリリース時にOffへ変更してください


## nodeセットアップ

[インストールURL](https://nodejs.org/ja/)

- version 10.15.3LTS

インストール後の確認

```
 $ node -v
 v10.15.3
 $ npm -v
 v3.10.10
```

## sailsのインストール

```
 $ npm install -g sails
 $ npm install -g sequelize-cli
```

```
 $ sails -v
 1.0.2
```

## ソースの取得

```
 $ git clone https://github.com/ics-opendev/sails-ttc.git
```

## local.js の配置

別途配布の local.js を `config/local.js` に配置。

## アプリの実行

```
 $ cd sails-ttc
 $ npm install
 $ npm audit fix
 $ sails lift
```

## 起動確認

[localhost](http://localhost:1337)

## PR 時のチェックを通過するための事前チェック

作業ブランチがマージされるためには、 lint, test のチェックを通過する必要があります。通過して緑色のチェックマークがつくまで、レビュワーはレビューをしません。 PR すれば自動でチェックされますが、ローカルでも以下のコマンドで自らチェックが可能です。

```bash
# Docker 起動
docker-compose up -d; docker exec -it node /bin/ash;

# sails-ttc のリポジトリに移動
cd /app/sails-ttc;

# lint の確認。
npm run lint

# test の確認。
npm run test
```

## 自動チェックでコケたときのエラー内容確認

1. Slack ログのリンクから DevOps へ go。
1. 失敗したテストには x マークがつくため、そこからチェック。
    - 権限不足のときは「権限を要求する」というようなリンクが表示されるはずです。そこから権限要求メールをプロジェクト管理者へ送ってください。

![devops](https://user-images.githubusercontent.com/28250432/100413954-f4434900-30bb-11eb-93fb-c0a22cadd22f.png)

## 各アプリケーションのバージョン更新時に確認する事

アプリケーションのバージョンを更新した際は下記テーブルの更新を行ってください
`ApplicationVersion`

各アプリケーションのリポジトリを記載
+ [Windows](https://github.com/ics-opendev/taskal-timecard-monitoring-for-windows)
+ [iPhone](https://github.com/ics-opendev/ICSFaceReader)

### Links

+ [Get started](https://sailsjs.com/get-started)
+ [Sails framework documentation](https://sailsjs.com/documentation)
