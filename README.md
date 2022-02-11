# taskal-timecard-thermometer

TTC(ios) の 体温測定拡張 アプリケーションです。

## OS install

[Raspberry Pi OS with desktop](https://www.raspberrypi.org/software/)をダウンロード

balenaEtcher をインストールして、
Raspberry Pi OS with desktop and recommended software をインストールする

## os setup

初期ユーザ
loginUser : pi
password : raspberry

初期パスワードから変更

```
$ passwd
```

変更後パスワード : Icsoft123

SSH はリリース時に Off へ変更してください

Wifi へ接続

この[サイト](http://www.openspc2.org/reibun/RaspberryPI/OS/Raspbian/etc/0002/index.html)を参考に IP を確認

### 画面インストール

```
$ cd ~
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

# bluetooth が一時的に利用できなくなるため、この修正を追加

https://github.com/waveshare/LCD-show/issues/43

### edit /boot/cmdline.txt and replace

vi は x で 1 文字消し

```
$ sudo vi /boot/cmdline.txt
$ console=ttyAMA0,115200 -> console=serial0,115200
```

```
# 再起動とインストールが入ります
$ sudo reboot
```

## app install

アプリのインストール

```
$ cd ~
$ cd taskal-timecard-thermometer
$ sudo chmod 777 *
$ sudo ./setup.sh
$ sudo cp start.sh /home/pi/Desktop
$ reboot
```

# 警告が邪魔な場合（非推奨）

```
$ sudo apt remove lxplug-ptbatt -y

$ sudo vi /boot/config.txt
# config.txtファイルを管理者権限で開いて 1行を追記
$ avoid_warnings=1
```

# TeamViewer のダウンロード (Raspiberry Version)

```
$ cd ~
$ sudo wget https://download.teamviewer.com/download/linux/teamviewer_armhf.deb
$ sudo chmod 777 teamviewer_armhf.deb
$ sudo apt install ./teamviewer_armhf.deb -y
$ sudo teamviewer setup
```

## app autostart

```
$ su
$ sudo echo '@lxterminal --command="/home/pi/taskal-timecard-thermometer/start.sh"' >> /etc/xdg/lxsession/LXDE-pi/autostart
```

## お客様の wifi に自動接続を行う

お客様より SSID と PW を受け取っている場合に限り事前に登録することができます
仮にお客様から受け取った情報が下記の場合の例を示す
SSID: "testSSID"
パスワード: 123456789

```

$ wpa_passphrase ${SSID}
この後パスワードの入力を求められます

network={
	ssid="testSSID"
	#psk="12345678"
	psk=aff6ecef59e550c27a16fa07f9451b9628d73ca974e83cdb50addfb3a3249fa9
}

#pskを消す

$ sudo vi wpa_supplicant.conf

末端を vi の oコマンドで改行し貼り付けを行う

```
