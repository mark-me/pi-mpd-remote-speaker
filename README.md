# pi-mpd-touchscreen

A Raspberry Pi view on what is being played by a MPD server. Used in combination with [snapcast](https://github.com/badaix/snapcast) to use the Pi as a remote speaker system. The current name of the project is misleading, since I've stripped the project from all touchscreen interactions.

## Install OH-MY-ZSH

Why? Does it add to the functionality? No. It's just nice to have ;-).

```bash
sudo apt install curl wget git
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
git clone https://github.com/zsh-users/zsh-autosuggestions.git $ZSH_CUSTOM/plugins/zsh-autosuggestions
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git $ZSH_CUSTOM/plugins/zsh-syntax-highlighting
nano ~/.zshrc
```

## Install snapclient

This does add to the functionality: it is the service that picks up playing music streams for multi-room audio.

```bash
sudo apt install snapclient -y
sudo service snapclient enable
sudo service snapclient start
```

## Install app

### Git

Clone git and remember credentials

```bash
git config --global user.name "Mark Zwart"
git config --global user.email "mark.zwart@pobox.com"
git config credential.helper store
git clone https://github.com/mark-me/pi-mpd-touchscreen.git
```

Create virtual environment

```bash
sudo apt install portaudio19-dev
sudo apt install python3-pip python3-virtualenv -y
cd pi-mpd-touchscreen
virtualenv .env
source .env/bin/activate
pip install -r requirements.txt
```

Create autostart for LXDE desktop

```bash
mkdir /home/mark/.config/autostart
nano /home/mark/.config/autostart/music.desktop
```

```
nano /home/mark/.config/autostart/music.desktop
```

```bash

nano .config/lxsession/LXDE-pi/autostart
```

or

```bash
sudo nano /etc/xdg/lxsession/LXDE-pi/autostart
```

Add entry

```
@bash /home/mark/pi-mpd-touchscreen/run.sh
```

### KDE Connect

Create autostart link

```
mkdir /home/mark/.config/autostart
nano /home/mark/.config/autostart/kdeconnect.desktop
```

Add to file

```
[Desktop Entry]
Type=Application
Name=KDE Connect
Exec=/usr/bin/kdeconnect-indicator
```

reboot

Connect

```
kdeconnect-cli -l
kdeconnect-cli --pair --device <device-id>
```
