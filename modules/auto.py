#!/usr/bin/env python
# coding: utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import time
import commands,requests
import string
import callback 
import uuid
import logging
import re

##log
#logging.basicConfig(level=logging.INFO,
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(levelname)-5s %(filename)s[line:%(lineno)d] %(message)s',
                filename='/letv/server/logs/auto_publish/out.log',
                filemode='a')

def rsync(id,src_path,dst_path,full=""):
    full = "--delete" if full == "full" else ""
    cmd = "rsync -aP %s %s %s" % (full,src_path,dst_path)
    logging.debug("%s %s" % (id,cmd)) 
    status,result = commands.getstatusoutput(cmd)
    if status:
        logging.error("%s %s" % (id,result))
        return result
    #else:
    #    logging.debug("%s %s" % (id,result))
    

def ssh_cmd(id,ip,cmds):
    cmd = "ssh %s '%s'" % (ip,cmds)
    logging.debug("%s %s" % (id,cmd)) 
    status,result = commands.getstatusoutput(cmd)
    if status:
        logging.error("%s %s" % (id,result))
        return result
    #else:
    #    logging.debug("%s %s" % (id,result))


def install_tomcat(id,ip,app_name,port):
    uid = uuid.uuid1() 
    result = rsync(id,'./packages/tomcat/','root@%s:/letv/public/soft/tomcat_%s/' % (ip,uid),'full')
    if result:
        logging.error("%s Tomcat安装包上传失败 %s %s %s" % (id,ip,app_name,port))
        return result
    else:
        logging.info("%s Tomcat安装包上传成功 %s %s %s" % (id,ip,app_name,port))
        cmd = 'cd /letv/public/soft/tomcat_%s && sh install_tomcat.sh %s %s' % (uid,app_name,port)
        ssh_result =  ssh_cmd(id,ip,cmd)
        if ssh_result:
            logging.error("%s Tomcat安装失败 %s %s %s" % (id,ip,app_name,port))
            return  ssh_result
        else:
            logging.info("%s Tomcat安装成功 %s %s %s" % (id,ip,app_name,port))


def uninstall_tomcat(id,ip,app_name,port):
    uid = uuid.uuid1() 
    result = rsync(id,'./packages/tomcat/uninstall_tomcat.sh','root@%s:/letv/public/soft/tomcat_%s/' % (ip,uid),'full')
    if result:
        logging.error("%s Tomcat卸载脚本上传失败 %s %s %s" % (id,ip,app_name,port))
        return result
    else:
        logging.info("%s Tomcat卸载脚本上传成功 %s %s %s" % (id,ip,app_name,port))
        cmd = 'cd /letv/public/soft/tomcat_%s/ && sh uninstall_tomcat.sh %s %s' % (uid,app_name,port)
        ssh_result =  ssh_cmd(id,ip,cmd)
        if ssh_result:
            logging.error("%s Tomcat卸载失败 %s %s %s" % (id,ip,app_name,port))
            return  ssh_result
        else:
            logging.info("%s Tomcat卸载成功 %s %s %s" % (id,ip,app_name,port))
            #return  ssh_result
    
def control_tomcat(id,ip,app_name,port,control):
    result = ssh_cmd(id,ip,'/etc/init.d/tomcat_%s_%s %s' % (app_name,port,control))
    if result:
        logging.error("%s Tomcat %s失败 %s %s %s" % (id,control,ip,app_name,port))
        return result
    else:
        logging.info("%s Tomcat %s成功 %s %s %s" % (id,control,ip,app_name,port))

def control_dubbo(id,ip,app_name,port,control):
    result = ssh_cmd(id,ip,'source /etc/profile;cd /letv/deployment/%s/bin;sh %s.sh' % (app_name,control))
    if result:
        logging.error("%s Dubbo %s失败 %s %s %s" % (id,control,ip,app_name,port))
        return result
    else:
        logging.info("%s Dubbo %s成功 %s %s %s" % (id,control,ip,app_name,port))

def pull_code(id,rel_id,svn_url,app_name,diy=""):
    uid = uuid.uuid1()
    if "," in svn_url:
        svn = eval(svn_url)
        svn_1 = svn[0]
        svn_2 = svn[1]
        cmd = 'svn export --username ops_shop --password shop_ops %s ../tmp/%s_%s_%s%s && svn export --force --username ops_shop --password shop_ops %s ../tmp/%s_%s_%s%s' % (svn_1,rel_id,app_name,uid,diy,svn_2,rel_id,app_name,uid,diy)
    elif not re.match('svn.letv.cn', svn_url):
        cmd = 'mkdir ../tmp/%s_%s_%s%s && wget -q %s -P ../tmp/%s_%s_%s%s' % (rel_id,app_name,uid,diy,svn_url,rel_id,app_name,uid,diy)
    else:
        cmd = 'svn export --username ops_shop --password shop_ops %s ../tmp/%s_%s_%s%s' % (svn_url,rel_id,app_name,uid,diy)
    logging.debug("%s %s" % (id,cmd))
    status,result = commands.getstatusoutput(cmd)
    logging.info("%s %s" % (status, result))
    local_path = '../tmp/%s_%s_%s' % (rel_id,app_name,uid)
    if status:
        logging.error("%s 代码拉取失败 %s SVN:%s %s" % (id,app_name,svn_url,result))
        return status,result,local_path
    else:
        logging.info("%s 代码拉取成功 %s SVN:%s" % (id,app_name,svn_url))
        return status,result,local_path

def pull_conf(svn_url):
    id=""
    rel_id=""
    app_name=""
    #confs = ['/WEB-INF/classes/conf/','/WEB-INF/classes/spring/']
    confs = ['/WEB-INF/classes/conf/','/conf/']
    lis=[]
    for i in confs:
        conf_url = svn_url + i 
        cmd = 'svn list --username ops_shop --password shop_ops %s '% (conf_url)
        logging.debug("%s" % (cmd))
        status,result = commands.getstatusoutput(cmd)
        if not status:
            status,result,local_path = pull_code(id,rel_id,conf_url,app_name,i)
            if not status:
                lis.append(local_path) 
    if len(lis) >0:
        return lis

def rollback_pull_code(id,rel_id,svn_url,app_name):
    uid = uuid.uuid1()
    rollback_id = svn_url
    cmd = 'unzip ./backup/%s_%s.zip -d ../tmp/%s_%s_%s' % (rollback_id,app_name,rel_id,app_name,uid)
    logging.debug("%s %s" % (id,cmd))
    status,result = commands.getstatusoutput(cmd)
    local_path = './tmp/%s_%s_%s/%s_%s/' % (rel_id,app_name,uid,rollback_id,app_name)
    if status:
        logging.error("%s 回滚文件:%s_%s.zip 回滚代码获取失败,%s" % (id,rollback_id,app_name,result))
        return status,result,local_path
    else:
        logging.info("%s 回滚文件:%s_%s.zip 回滚代码获取成功" % (id,rollback_id,app_name))
        return status,result,local_path
    
def backup_code(id,rel_id,ip,app_name):
    result = rsync(id,'root@%s:/letv/deployment/%s/' % (ip,app_name),'./backup/%s_%s/' % (rel_id,app_name))
    if result:
        logging.error("%s 代码备份失败 %s %s" % (id,ip,app_name))
        return result
    else:
        commands.getstatusoutput('pwd') 
        cmd = ('cd ./backup && zip -rm {0}_{1}.zip {0}_{1} && cd ../'.format(rel_id,app_name))
        logging.debug("%s %s" % (id,cmd))
        status,result = commands.getstatusoutput(cmd)
        if status:
            logging.error("%s 代码备份失败 %s %s %s" % (id,ip,app_name,result))
            return result
        else:
            logging.info("%s 代码备份成功 %s %s" % (id,ip,app_name))

def push_code(id,local_dir,ip,app_name,full=""):
    if full != "full":
        full = ""
        tag="增量"
    else:
        tag="全量"
    result = rsync(id,'%s/' % (local_dir),'root@%s:/letv/deployment/%s/' % (ip,app_name),'%s' % (full))
    if result:
        logging.error("%s %s代码上传失败 %s %s" % (id,tag,ip,app_name))
        return result
    else:
        logging.info("%s %s代码上传成功 %s %s" % (id,tag,ip,app_name))

def del_code(id,rel_id,ip,app_name,port):
    #result = backup_code(id,rel_id,ip,app_name)
    #if result:
    #    logging.error("%s 代码删除失败 %s %s" % (id,ip,app_name))
    #    return result
    #else:
    #    control_tomcat(id,ip,app_name,port,'stop')
    ssh_result = ssh_cmd(id,'%s' % (ip),'cd /letv/deployment/ && rm -rf %s' % (app_name))    
    if ssh_result:
        logging.error("%s 代码删除失败 %s %s" % (id,ip,app_name))
        return ssh_result
    else:
        logging.info("%s 代码删除成功 %s %s" % (id,ip,app_name)) 

def publish(id,rel_id,ip,app_name,port,local_path,state,container,full=""):
    tag = "全量" if full == "full" else "增量"
    r = requests.get('http://res.lemall.com/check_rel?rel_id=' + str(rel_id) )
    #停止 tomcat
    if r.text == "no first" and (state != "备" or u"备"):
    #if state != "备" or u"备":
        callback.callback(rel_id,ip,port,"停止容器","update")
        if container == "tomcat":
            result = control_tomcat(id,ip,app_name,port,'stop')
        elif container == "dubbo" or container == '其他':
            result = control_dubbo(id,ip,app_name,port,'stop')
    else:
        result = ""
    if result:
        logging.error("%s 发版失败[%s] %s %s %s" % (id,tag,ip,app_name,port))
        callback.callback(rel_id,ip,port,"停止容器失败","update")
        return result
    else: 
        #上传代码
        callback.callback(rel_id,ip,port,"上传代码","update")
        result = push_code(id,local_path,ip,app_name,full)
        if result:
            logging.error("%s 发版失败[%s] %s %s %s" % (id,tag,ip,app_name,port))
            callback.callback(rel_id,ip,port,"上传代码失败","update")
            return result
        else:
            #启动 tomcat
            if state != "备" or u"备":
                callback.callback(rel_id,ip,port,"启动容器","update")
                if container == "tomcat":
                    result = control_tomcat(id,ip,app_name,port,'start')
                elif container == "dubbo" or container == '其他':
                    result = control_dubbo(id,ip,app_name,port,'start')
            else:
                result = ""

            if result:
                logging.error("%s 发版失败[%s] %s %s %s" % (id,tag,ip,app_name,port))
                callback.callback(rel_id,ip,port,"启动容器失败","update")
                return result
            else:
                #完成
                logging.info("%s 发版完成[%s] %s %s %s" % (id,tag,ip,app_name,port))
                callback.callback(rel_id,ip,port,"完成","update")
                return result

del_list = []
def delete_server(id,app_id,ip,app_name,port):
    global del_list
    uid = uuid.uuid1()
    control_tomcat(id,ip,app_name,port,'stop')
    uninstall_tomcat(app_id,ip,app_name,port)
    del_code(id,app_id,ip,app_name,port)

    result = rsync(id,'./packages/tomcat/check_uninstall_tomcat.sh','root@%s:/letv/public/soft/tomcat_%s/' % (ip,uid),'full')
    if result:
        logging.error("%s Tomcat检查脚本上传失败 %s %s %s" % (id,ip,app_name,port))
        del_list.append([[ip,port,"fail"]])
        return result
    else:
        logging.info("%s Tomcat检查脚本上传成功 %s %s %s" % (id,ip,app_name,port))
        cmd = 'cd /letv/public/soft/tomcat_%s/ && sh check_uninstall_tomcat.sh %s %s' % (uid,app_name,port)
        ssh_result =  ssh_cmd(ip,ip,cmd)
        if ssh_result:
            del_list.append([ip,port,"fail"])
            logging.error("%s Tomcat未完全卸载%s %s %s" % (id,ip,app_name,port))
            return  ssh_result
        else:
            del_list.append([ip,port,"success"])

    #del_list.append([ip,"fail"])
    #del_list.append([ip,"success"])
    #result = del_code(id,app_id,ip,app_name,port)
    #logging.error("%s 下架失败 %s %s %s" % (app_id,ip,app_name,port))        
    #logging.info("%s 下架成功 %s %s %s" % (app_id,ip,app_name,port))


if __name__ == '__main__':
    id = "000"
    rel_id = "001"
    port = "1234"
    app_name = "dubbo_letv-oss-order" 
    ip = "10.135.28.200"
    local_path="../packages/test/"
    svn_url = "46"
    svn_url = "http://svn.letv.cn/lemall/ops/code/test/1.0.0.0/"
    svn_url = "http://svn.letv.cn/lemall/ops/code/test/dubbo_letv-oss-order/"
    container = "dubbo"
    status = "" 
    #print install_tomcat(id,ip,app_name,port)
    #print uninstall_tomcat(id,ip,app_name,port)
    #print control_tomcat(id,ip,app_name,port,'stop')
    #print control_tomcat(id,ip,app_name,port,'start')
    #print pull_code(id,rel_id,svn_url,app_name)
    #print rollback_pull_code(id,rel_id,'46',app_name)
    #print backup_code(id,rel_id,ip,app_name)
    #print push_code(id,local_path,ip,app_name)
    #print push_code(id,local_path,ip,app_name,'full')
    #print del_code(id,rel_id,ip,app_name,port)
    #print publish(id,rel_id,ip,app_name,port,local_path)
    #print publish(id,rel_id,ip,app_name,port,local_path,'full')
    ##print check_tomcat(id,ip,port,app_name)

    #print delete_server(id,rel_id,ip,app_name,port)
    #print pull_conf(svn_url)

    #模拟全量发版 
    #print install_tomcat(id,ip,app_name,port)
    #print publish(id,rel_id,ip,app_name,port,local_path,status,container,'full')
    #print uninstall_tomcat(id,ip,app_name,port)

