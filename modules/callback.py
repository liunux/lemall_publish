#!/usr/bin/env python
#coding:utf-8

import requests

def callback(rel_id,ip,port,status,type):
    callback_url = "http://res.lemall.com/rel_publish"
    callback_url = "http://10.58.74.204:8001/rel_publish"
    callback_ask={"rel_id":rel_id,"ip":ip,"port":port,"status":status,"type":type}
    callback_r = requests.post(callback_url,data = callback_ask)
