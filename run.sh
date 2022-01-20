#! /bin/bash

case $SSH_CONNECTION in
  '')
  cd pi-mpd-touchscreen
  python3 pi-mpd-touchscreen.py
  cd .. ;;
esac

