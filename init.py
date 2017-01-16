#!/usr/bin/env python
#coding:utf-8

import uuid
import commands,requests
import threading
import sys
sys.path.append("./modules")
import auto
import sub
import callback
from flask import Flask, app, request, render_template, redirect, url_for, session, abort, jsonify, make_response, send_from_directory, make_response
from log import *

##log
#logging.basicConfig(level=logging.INFO,
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(levelname)-5s %(filename)s[line:%(lineno)d] %(message)s',
                #filename='/letv/server/logs/auto_publish/out.log',
                #filename='./out.log',
                filename='/letv/server/logs/auto_publish/run_log/%s' % id,
                filemode='a')


app = Flask(__name__)

@app.route('/publish',methods=['POST', 'GET'])
def call_publish():
    if request.method == 'POST':
        rel_id = request.values.get('rel_id','')
        app_type = request.values.get('app_type','')
        app_version= request.values.get('app_version','')
        app_name = request.values.get('app_name','')
        container = request.values.get('container','')
        svn_url = request.values.get('app_svn','')
        ip_info = eval(request.values.get('ipinfo',''))
        backup_ip=ip_info[0][0]
        backup_port=ip_info[0][1]
        
        for i in ip_info:
            ip,port = i[0],i[1]
            callback.callback(rel_id,ip,port,"代码拉取","update")
        id = "ID:%s_%s>" % (rel_id,app_name) 
        #get代码
        if app_type == u"回滚":
            app_type="full"
            status,result,local_path = auto.rollback_pull_code(id,rel_id,svn_url,app_name)
        elif app_type == u"全量": 
            app_type="full"
            status,result,local_path = auto.pull_code(id,rel_id,svn_url,app_name)
        elif app_type == "ci_publish":
            app_type="full"
            status,result,local_path = auto.pull_code(id,rel_id,app_version,app_name)
        else:
            status,result,local_path = auto.pull_code(id,rel_id,svn_url,app_name)


        #backup代码
        if not status:
            callback.callback(rel_id,backup_ip,backup_port,"代码备份","update")
            r = requests.get('http://res.lemall.com/check_rel?rel_id=' + str(rel_id) )
            print "r:",r.text
            if r.text == 'no first':
                result = auto.backup_code(id,rel_id,backup_ip,app_name)
            else:
                result = "" 

            #多线程publish
            ########length = len(ip_info)
            if not result:
                threads = []
                for i in ip_info:
                    ip,port,state = i[0],i[1],[2]
                    id = "ID:%s_%s-%s-%s>" % (rel_id,app_name,ip,port)
                    t1 = threading.Thread(target=auto.publish,args=(id,rel_id,ip,app_name,port,local_path,state,container,app_type))
                    threads.append(t1)
                for t in threads:
                    t.setDaemon(True)
                    t.start()
                for t in threads:
                    t.join()
                return "0"
            else:
                callback.callback(rel_id,ip,port,"代码备份失败","update")
                return  "1"
        else:
            callback.callback(rel_id,ip,port,"代码拉取失败","update")
            return "1" 
    else:
        return 'Error: Pls use POST !!!'

@app.route('/software',methods=['POST', 'GET'])
def software():
    if request.method == 'POST':
        #mode = request.values.get('mode','')
        ip_info = eval(request.values.get('ipinfo',''))
        port = request.values.get('port', '')
        app_id = request.values.get('app_id','')
        app_name = request.values.get('app_name','')
        software = request.values.get('software','')
        software_mode = request.values.get('software_mode','')
        if software == "tomcat" and software_mode == "install":
            function =  auto.install_tomcat
        elif software == "tomcat" and software_mode == "uninstall":
            function =  auto.uninstall_tomcat
        else:
            return '"message":"调用错误，此方法不存在！","status":"1"'
        threads = []
        for i in ip_info:
            ip,port = i[0],i[1]
            id = "ID:%s_%s-%s-%s>" % (app_id,app_name,ip,port)
            t1 = threading.Thread(target=function,args=(id,ip,app_name,port))
            threads.append(t1)
        for t in threads:
            t.setDaemon(True)
            t.start()
        for t in threads:
            t.join()

        return "0"
    else:
        return '"message":"Pls use POST mode!","status":"1"'


@app.route('/software_check',methods=['POST'])
def software_check():
    lis = []
    def check_tomcat(id,ip,port,app_name):
        uid = uuid.uuid1()
        result = auto.rsync(id,'./packages/tomcat/check_install_tomcat.sh','root@%s:/letv/public/soft/tomcat_%s/' % (ip,uid),'full')
        if result:
            logging.error("%s Tomcat检查脚本上传失败 %s %s %s" % (id,ip,app_name,port))
            return result
        else:
            logging.info("%s Tomcat检查脚本上传成功 %s %s %s" % (id,ip,app_name,port))
            cmd = 'cd /letv/public/soft/tomcat_%s/ && sh check_install_tomcat.sh %s %s' % (uid,app_name,port)
            ssh_result =  auto.ssh_cmd(id,ip,cmd)
            if ssh_result:
                lis.append([id,"fail"])
                logging.error("%s Tomcat安装状态Error %s %s %s" % (id,ip,app_name,port))
                return  ssh_result
            else:
                lis.append([id,"success"])
                logging.info("%s Tomcat安装状态ok %s %s %s" % (id,ip,app_name,port))

    ip_info = eval(request.values.get('ipinfo',''))
    software = request.values.get('software','') 
    app_name = request.values.get('app_name','') 
    if software == "tomcat":
        function = check_tomcat
    else:
        return '"message":"调用错误，此方法不存在！","status":"1"'
    threads = []
    for i in ip_info:
        id,ip,port = i[0],i[2],i[3]
        t1 = threading.Thread(target=function,args=(id,ip,port,app_name))
        threads.append(t1)
    for t in threads:
        t.setDaemon(True)
        t.start()
    for t in threads:
        t.join()
    return  "%s" % lis 

@app.route('/query_log',methods=['POST', 'GET'])
@app.route('/',methods=['POST', 'GET'])
def query_log():
    id = request.values.get('id','')
    rel_id = request.values.get('rel_id','')
    app_name = request.values.get('app_name','')
    ip = request.values.get('ip','')
    port = request.values.get('port','')
    key1 = "ID:%s_%s-%s-%s>" % (rel_id,app_name,ip,port)
    key2 = "ID:%s_%s>" % (rel_id,app_name)   
    if rel_id == "*":
        status,result = commands.getstatusoutput('cat /letv/server/logs/auto_publish/out.log')
    else:
        status,result = commands.getstatusoutput('sh ./shell/query_log.sh  /letv/server/logs/auto_publish/out.log "%s" "%s"' % (key1,key2))
    if status:
        return "Error:key:%s log query is null !\n%s" % (id,result)
    else:
        return render_template('query.html',**locals())



@app.route('/delete_server',methods=['POST'])
def call_delete_server():
    id='0'
    app_id = request.values.get('app_id','')
    app_name = request.values.get('app_name','')
    ip_info = eval(request.values.get('ipinfo',''))
    backup_ip=ip_info[0][0]
    backup_port=ip_info[0][1]

    #backup代码
    auto.backup_code('0',app_id,backup_ip,app_name)

    #多线程删除
    threads = []
    auto.del_list = []
    for i in ip_info:
        ip,port,state = i[0],i[1],[2]
        id = "ID:%s_%s-%s-%s>" % (app_id,app_name,ip,port)
        t1 = threading.Thread(target=auto.delete_server,args=(id,app_id,ip,app_name,port))
        threads.append(t1)
    for t in threads:
        t.setDaemon(True)
        t.start()
    for t in threads:
        t.join()
    
    auto.del_list.sort(key=lambda x:x[0]) 
    #person = {"status":"0","message":"%s" % auto.del_list}
    #return jsonify(person=person)
    return '%s' % auto.del_list 

@app.route('/sub_key', methods=['POST','GET'])
def call_sub_key():
    svn_url = request.values.get('svn_url','')
    location = request.values.get('location','')
    env = request.values.get('env', '')
    result = sub.sub_key(svn_url,location,env)
    return result

#@app.route('/control_tomcat', methods=['POST'])
#def call_control_tomcat():
#    mode = request.values.get('mode','')
#    ip_info = eval(request.values.get('ipinfo',''))
#    port = request.values.get('port', '')
#    app_name = request.values.get('app_name','')
#    threads = []
#    for i in ip_info:
#        ip,port = i[0],i[1]
#        t1 = threading.Thread(target=auto.control_tomcat,args=(ip,app_name,port,mode))
#        threads.append(t1)
#    for t in threads:
#        t.setDaemon(True)
#        t.start()
#    return "0" 

if __name__ == '__main__':
    #app.config['DEBUG'] = True
    app.run(host='0.0.0.0', port=8002)
