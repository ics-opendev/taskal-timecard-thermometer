taskal-timecard-thermometer
===

TTC(ios) の 体温測定拡張 アプリケーションです。

## OS install

[Raspberry Pi OS Full](https://www.raspberrypi.org/software/)をダウンロード

セットアップアプリをインストールして、
Raspberry Pi OS Fullをインストールする

この[サイト](https://www.itmedia.co.jp/news/articles/2006/05/news031.html)を参考にどうぞ

## os setup

初期ユーザ
 loginUser : pi
 password  : raspberry

変更後パスワード : Icsoft123

SSHの有効化
この[サイト](https://qiita.com/tomokin966/items/bc22d09f97ebeb3955d2)を参考にどうぞ

SSHはリリース時にOffへ変更してください

## app install

アプリのインストール
```
git clone https://github.com/ics-opendev/taskal-timecard-thermometer.git
cd taskal-timecard-thermometer
sudo chmod 777 *
./setup.sh
```