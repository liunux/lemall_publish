#!/bin/sh
#install tomcat

[ -z $1 ] && echo  "error: 请输入服务名!" && exit 1
[ -z $2 ] && echo  "error: 请输入端口号!" && exit 1

app_name=$1
tomcat_port=$2
tomcat_home="/letv/server/tomcat_${app_name}_${tomcat_port}"
uninstall_package_home=$PWD

#判断是否安装
if [ ! -d $tomcat_home ] &&  [ ! -f /etc/init.d/tomcat_${app_name}_${tomcat_port} ];then
    echo "`date '+%Y%m%d %H:%M:%S'` ERROR:未安装tomcat_${app_name}_${tomcat_port}"|tee -a /root/init_zhixin.log
    rm -fr ${uninstall_package_home}
    exit 1
fi

#卸载
/etc/init.d/tomcat_$tomcat_${app_name}_${tomcat_port} stop
rm -rf ${tomcat_home}
rm -rf /etc/init.d/tomcat_$tomcat_${app_name}_${tomcat_port}

if [ ! -d $tomcat_home ] && [ ! -x /etc/init.d/tomcat_${app_name}_${tomcat_port} ] && [ `ps aux|grep -v grep|grep -c ${app_name}_${tomcat_port}` = 0 ];then
    echo "`date '+%Y%m%d %H:%M:%S'` tomcat_${app_name}_${tomcat_port}卸载成功"|tee -a /root/init_zhixin.log
    #权限控制
    rm -fr ${uninstall_package_home}
    exit 0
else
    echo "`date '+%Y%m%d %H:%M:%S'` tomcat_${app_name}_${tomcat_port}卸载失败"|tee -a /root/init_zhixin.log
    rm -fr ${uninstall_package_home}
    exit 1
fi
