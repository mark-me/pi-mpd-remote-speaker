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
    python3 pi-mpd-touchscreen.py  >> logfile.log 2>&1
    deactivate
    writelog "Exited with status $?"
    writelog "Restarting"
    deactivate
  done
  cd .. ;;
esac
