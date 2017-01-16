#!/bin/bash
[ -z $1 ] && echo  "Usage: check_install_tomcat.sh app_name port" && exit 1
[ -z $2 ] && echo  "Usage: check_install_tomcat.sh app_name port" && exit 1

app_name=$1
tomcat_port=$2
tomcat_home="/letv/server/tomcat_${app_name}_${tomcat_port}"

if [ -d $tomcat_home ];then
    if [ -x /etc/init.d/tomcat_${app_name}_${tomcat_port} ];then
        if [ -d /letv/deployment/${app_name} ];then
            echo "ok:tomcat_${app_name}_${tomcat_port} is Successful installation"
            exit 0
        else
            echo "Error:/letv/deployment/${app_name} ,No such directory !"
            exit 4
        fi
    else
        echo "Error:/etc/init.d/tomcat_${app_name}_${tomcat_port} ,Can not run !"
        exit 3
    fi
else
    echo "Error:$tomcat_home ,No such directory !"
    exit 2
fi
