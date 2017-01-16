#!/bin/sh
#install tomcat

[ -z $1 ] && echo  "error: 请输入服务名!" && exit 1
[ -z $2 ] && echo  "error: 请输入端口号!" && exit 1

app_name=$1
tomcat_port=$2
tomcat_home="/letv/server/tomcat_${app_name}_${tomcat_port}"
install_package_home=$PWD
tomcat_version=`ls $install_package_home|grep apache-tomcat.*zip|sed 's/\(.*\).zip/\1/g'`

#判断是否安装
if [ -d $tomcat_home ] &&  [ -x /etc/init.d/tomcat_${app_name}_${tomcat_port} ];then
    echo "`date '+%Y%m%d %H:%M:%S'` ERROR:已安装tomcat_${app_name}_${tomcat_port}"|tee -a /root/init_zhixin.log
    rm -fr ${install_package_home}
    exit 1
fi

#添加hosts
if [[ -z `grep "$(hostname)" /etc/hosts` ]];then
    sed -i "/127.0.0.1/s/$/ $(hostname)/g" /etc/hosts
    sed -i "/::1/s/$/ $(hostname)/g" /etc/hosts
fi



#安装tomcat
cd ${install_package_home}
unzip ${tomcat_version}.zip
unzip conf.zip

mkdir -p /letv/deployment/$app_name
mv ${tomcat_version} ${tomcat_home}

rm -fr ${tomcat_home}/webapps/*
sed -i "s/8080/${tomcat_port}/g" ${install_package_home}/server.xml
sed -i "s/example_app/${app_name}/g" ${install_package_home}/server.xml
rsync -aP ${install_package_home}/server.xml ${tomcat_home}/conf/server.xml

rsync -aP ${install_package_home}/catalina.sh ${tomcat_home}/bin/catalina.sh

sed -i "s/8080/${app_name}_${tomcat_port}/g" ${install_package_home}/tomcat_8080
rsync -aP ${install_package_home}/tomcat_8080 /etc/init.d/tomcat_${app_name}_${tomcat_port}

chmod 770 /etc/init.d/tomcat_${app_name}_${tomcat_port}
chown lemall /etc/init.d/tomcat_${app_name}_${tomcat_port}
chkconfig --level 2345 tomcat_${app_name}_${tomcat_port} on

chown -R lemall.lemall ${tomcat_home}/
chmod -R 775 ${tomcat_home}/
chmod -R 774 ${tomcat_home}/bin/


if [ -d $tomcat_home ] &&  [ -x /etc/init.d/tomcat_${app_name}_${tomcat_port} ];then
    echo "`date '+%Y%m%d %H:%M:%S'` tomcat_${app_name}_${tomcat_port}安装成功"|tee -a /root/init_zhixin.log
    #权限控制
    rm -fr ${install_package_home}
    exit 0
else
    echo "`date '+%Y%m%d %H:%M:%S'` tomcat_${app_name}_${tomcat_port}安装失败"|tee -a /root/init_zhixin.log
    rm -fr ${install_package_home}
    exit 1
fi
