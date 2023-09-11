#! /bin/bash

cd /home/mark/pi-mpd-touchscreen

LOGFILE=restart.txt

writelog() {
  now=`date`
  echo "$now $*" >> $LOGFILE
}

case $SSH_CONNECTION in
  '')
  writelog "Starting"
  while true ; do
    source ".venv/bin/activate"
    python3 main.py >> logfile.log 2>&1
    deactivate
    writelog "Exited with status $?"
    writelog "Restarting"
    deactivate
  done
  cd .. ;;
esac
