#!/bin/bash
Cur_Dir=$(pwd)
gunicorn --worker-class=gevent -w 4 ../init:app -b 0.0.0.0:8888 --access-logfile ${Cur_Dir}/../logs/access.log  --log-file ${Cur_Dir}/../logs/start.log -p $Cur_Dir/init.pid &
