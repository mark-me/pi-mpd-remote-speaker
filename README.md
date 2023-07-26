# pi-mpd-touchscreen
Touchscreen controller for MPD server

## Install screen
```
sudo nano /boot/config.txt
```
Add
```
hdmi_group=2
hdmi_mode=87
hdmi_cvt 480 800 60 6 0 0 0
dtoverlay=ads7846,cs=1,penirq=25,penirq_pull=2,speed=50000,keep_vref_on=0,swapxy=0,pmax=255,xohms=150,xmin=200,xmax=3900,ymin=200,ymax=3900
display_rotate=3
```

## Install snapclient
```
sudo apt install snapclient -y
sudo service snapclient enable
sudo service snapclient start
```



## Install app

### Git

```
git config --global user.name "Mark Zwart"
git config --global user.email "mark.zwart@pobox.com"
git clone https://github.com/mark-me/pi-mpd-touchscreen.git
```

```
sudo apt install python3-pip python3-virtualenv -y
cd pi-mpd-touchscreen
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```
