#! /bin/bash

LOGFILE=restart.txt

writelog() {
  now=`date`
  echo "$now $*" >> $LOGFILE
}

case $SSH_CONNECTION in
  '')
  writelog "Starting"
  cd pi-mpd-touchscreen
  while true ; do
    source ".venv/bin/activate"
    python3 pi-mpd-touchscreen.py
    deactivate
    writelog "Exited with status $?"
    writelog "Restarting"
  done
  cd .. ;;
esac
