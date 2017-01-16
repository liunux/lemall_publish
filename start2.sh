#!/bin/bash
#Cur_Dir=$(pwd)
Cur_Dir='/letv/server/logs/auto_publish'
[[ ! -d $Cur_Dir ]] && mkdir -p $Cur_Dir
nohup gunicorn --worker-class=gevent -w 4 init:app -b 0.0.0.0:8002 --access-logfile ${Cur_Dir}/access.log  --log-file ${Cur_Dir}/start.log -p ./init.pid2 &
