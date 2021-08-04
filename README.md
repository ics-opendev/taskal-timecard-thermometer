taskal-timecard-thermometer
===

TTC(ios) の 体温測定拡張 アプリケーションです。

## OS install

[Raspberry Pi OS with desktop](https://www.raspberrypi.org/software/)をダウンロード

balenaEtcherをインストールして、
Raspberry Pi OS with desktop and recommended softwareをインストールする

## os setup

初期ユーザ
 loginUser : pi
 password  : raspberry

変更後パスワード : Icsoft123

SSHの有効化
この[サイト](https://qiita.com/tomokin966/items/bc22d09f97ebeb3955d2)を参考にどうぞ

SSHはリリース時にOffへ変更してください

Wifi へ接続

この[サイト](http://www.openspc2.org/reibun/RaspberryPI/OS/Raspbian/etc/0002/index.html)を参考にIPを確認

TeamViewerのダウンロード (Raspiberry Version)
↓
高橋アカウントでログイン

### 画面インストール

LCD-show.tar.gz をdownloadに配置

```
$ cd /home/pi/Downloads
$ sudo cp LCD-show.tar.gz /boot
$ sudo passwd root
$ sudo su -
$ cd /boot
$ sudo tar zxvf LCD-show.tar.gz
# backup
$ sudo cp config.txt ./LCD-show/boot
$ cd LCD-show/
```

# bluetoothが一時的に利用できなくなるため、この修正を追加
https://github.com/waveshare/LCD-show/issues/43

```

$ ./MPI3508-show
# 再起動とインストールが入ります
$ sudo passwd -l root
```


## app install

アプリのインストール
```
$ git clone https://github.com/ics-opendev/taskal-timecard-thermometer.git
$ cd taskal-timecard-thermometer
$ sudo chmod 777 *
$ sudo ./setup.sh
$ sudo cp start.sh /home/pi/Desktop
$ reboot
```

# 警告が邪魔な場合（非推奨）
https://qiita.com/nayuki_eng/items/3180da7ea0e4adab4e6c
