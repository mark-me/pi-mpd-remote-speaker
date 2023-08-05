# pi-mpd-touchscreen

A Raspberry Pi view on what is being played by a MPD server. Used in combination with [snapcast](https://github.com/badaix/snapcast) to use the Pi as a remote speaker system. The name of the project currently is misleading, since I've stripped the project from all touchscreen interactions.

## Install OH-MY-ZSH

```bash
sudo apt install curl wget git
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
git clone https://github.com/zsh-users/zsh-autosuggestions.git $ZSH_CUSTOM/plugins/zsh-autosuggestions
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git $ZSH_CUSTOM/plugins/zsh-syntax-highlighting
nano ~/.zshrc
```

## Install snapclient
```bash
sudo apt install snapclient -y
sudo service snapclient enable
sudo service snapclient start
```

## Install app

### Git

```bash
git config --global user.name "Mark Zwart"
git config --global user.email "mark.zwart@pobox.com"
git config credential.helper store
git clone https://github.com/mark-me/pi-mpd-touchscreen.git
```

```bash
sudo apt install python3-pip python3-virtualenv -y
cd pi-mpd-touchscreen
virtualenv .env
source .env/bin/activate
pip install -r requirements.txt
```
