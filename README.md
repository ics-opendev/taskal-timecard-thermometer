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

SSHはリリース時にOffへ変更してください

Wifi へ接続

この[サイト](http://www.openspc2.org/reibun/RaspberryPI/OS/Raspbian/etc/0002/index.html)を参考にIPを確認


### 画面インストール

LCD-show.tar.gz をdownloadに配置

```
$ git clone https://github.com/ics-opendev/taskal-timecard-thermometer.git
$ cd taskal-timecard-thermometer
$ sudo cp LCD-show.tar.gz /boot
$ sudo passwd root
$ sudo su -
$ cd /boot
$ sudo tar zxvf LCD-show.tar.gz
# backup
$ sudo cp config.txt ./LCD-show/boot
$ cd LCD-show/
$ ./MPI3508-show
```

TeamViewerのダウンロード (Raspiberry Version)
↓
高橋アカウントでログイン

# bluetoothが一時的に利用できなくなるため、この修正を追加
https://github.com/waveshare/LCD-show/issues/43

### edit /boot/cmdline.txt and replace

vi は x で1文字消し

```
$ console=ttyAMA0,115200 -> console=serial0,115200
```


```
# 再起動とインストールが入ります
$ sudo reboot
```


## app install

アプリのインストール
```
$ cd taskal-timecard-thermometer
$ sudo chmod 777 *
$ sudo ./setup.sh
$ sudo cp start.sh /home/pi/Desktop
$ reboot
```

## app autostart

自動起動の設定
https://qiita.com/karaage0703/items/ed18f318a1775b28eab4

```
$ su
$ sudo echo '@sleep 10s' >> /etc/xdg/lxsession/LXDE-pi/autostart
$ sudo echo '@bash /home/pi/taskal-timecard-thermometer/start.sh' >> /etc/xdg/lxsession/LXDE-pi/autostart
```

# 警告が邪魔な場合（非推奨）
https://qiita.com/nayuki_eng/items/3180da7ea0e4adab4e6c

```
$ sudo vi /boot/config.txt
# config.txtファイルを管理者権限で開いて 1行を追記
$ avoid_warnings=1
```