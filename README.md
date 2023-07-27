# pi-mpd-touchscreen
Touchscreen controller for MPD server

## Install screen

```
git clone https://github.com/waveshare/LCD-show.git
cd LCD-show
./LCD-hdmi
```

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
Edit rc.local
```
sudo nano /etc/rc.local
```
Add before exit 0
```
# disable console blanking on PiTFT
sudo sh -c "TERM=linux setterm -blank 0 >/dev/tty0"
```

## Install OH-MY-ZSH

```
sudo apt install curl wget git
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
git clone https://github.com/zsh-users/zsh-autosuggestions.git $ZSH_CUSTOM/plugins/zsh-autosuggestions
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git $ZSH_CUSTOM/plugins/zsh-syntax-highlighting
nano ~/.zshrc
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
