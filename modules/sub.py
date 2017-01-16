#!/usr/bin/env python
#coding:utf-8
import os
import re
import requests
import auto
from aes import *
pc = prpcrypt('yj_L]<xQ07zrOqlf')

def get_value(location,env,key):
    #url="http://res.lemall.com/rel_config"
    url="http://10.58.74.247:8001/query_key"
    ask={'location':location,
         'env':env,
         'key':key}
    r = requests.post(url,data=ask)
    if r.status_code == 200:
        d = pc.decrypt(r.text)
        return d


file_list=[]
def search(path):
    if os.path.isfile(path):
        file_list.append(path)
        return file_list
    elif os.path.isdir(path):
        for filename in os.listdir(path):
            fp = os.path.join(path, filename)
            if os.path.isfile(fp):
                file_list.append(fp)
            elif os.path.isdir(fp):
                search(fp)
        return file_list

def replace(location,env,files=[]):
    sub_lis={}
    for i in files:
        if "sub_keys.conf" in i:
            with open(i) as f:
                keylist = f.readlines()
                keylist = [x.strip() for x in keylist]
                #print "keylist:",keylist
    #for i in files:
    #    result = open(i).read()
        #key = re.findall('OPS-[^-\s]*-SPO', result)
        #key = re.findall('OPS-[a-zA-Z_]*-SPO', result)
    if keylist:
        for k in keylist:
            sub_lis[k] = "Fail"
            value = get_value(location,env,k)
            if value:
                for i in files:
                    result = open(i).read()
                    if k in result:
                        new_result = re.sub(k,value,result)
                        if "sub_keys.conf" not in i:
                            sub_lis[k] = "Success"
                        f=open(i,'w')
                        f.write(new_result)
                        f.close()
                #else:
                 #   sub_lis.append(["%-7s" % "Fail","%s:%s" % (i.split('/',3)[3],k)])
    #sub_lis.sort(key=lambda x:x[0])
    return sub_lis

def sub_key(svn_url,location,env):
    dir = auto.pull_conf(svn_url)
    if dir:
        for i in dir:
            files = search(i)
            if "sub_keys.conf" in str(files):
                result = replace(location,env,files)
                if result:
                    logging.info("Fail: %s [%s:%s]替换结果:%s" % (svn_url,location,env,result))
                    #s='\n'.join( [x[0]+' '+x[1] for x in result])
                    return result
                else:
                    logging.error("Fail: %s [%s:%s]未找到任何KEY!" % (svn_url,location,env))
                    return "Fail: %s [%s:%s]未找到任何KEY!" % (svn_url,location,env) 
            else:
                #return "Fail: %s [%s:%s]未找到配置文件['/WEB-INF/classes/conf/'或'/WEB-INF/classes/spring/']!" % (svn_url,location,env)
                return "Fail: %s [%s:%s]未找到配置文件'sub_keys.conf'!" % (svn_url,location,env)
                logging.error("Fail: %s [%s:%s]未找到任何文件['/WEB-INF/classes/conf/'或'/WEB-INF/classes/spring/']!" % (svn_url,location,env))
    else:
        return "Fail: %s [%s:%s]未找到配置目录['/WEB-INF/classes/conf/'或'/WEB-INF/classes/spring/']!" % (svn_url,location,env) 
        logging.error("Fail: %s [%s:%s]未找到配置目录['/WEB-INF/classes/conf/'或'/WEB-INF/classes/spring/']!" % (svn_url,location,env))

if __name__ == '__main__':
    location=u"大陆"
    env=u"预览"
    svn=u"http://svn.letv.cn/lemall/ops/code/test/dubbo_letv-oss-order/1.0.0.0/"
    #print replace('大陆','生产',files)
    #print get_value('大陆','生产','OPS-db_tms_r_passwd-SPO')
    print sub_key(svn,location,env)
