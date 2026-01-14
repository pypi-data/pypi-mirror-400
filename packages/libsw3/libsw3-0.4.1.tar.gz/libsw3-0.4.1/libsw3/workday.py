#!/usr/bin/python3
# -*- coding: utf8 -*-

__all__=["lastday","nextday","isworkday","是工作日","上一工作日","下一工作日","下一天","上一天"]

import time,base64,sys,json,urllib.request,ssl,os,datetime
import libsw3 as sw3

例外={}

def 获取例外数据():
    global 例外
    if sw3.swdb:
        for 类型,日期 in sw3.swdb.execute("select c_type,d_date from tworkday"):
            if 类型 not in 例外:例外[类型]=[]
            例外[类型].append(日期)
    else:
        try:
            url="https://swnweb.rt/oapi?method=workdaydata"
            context = ssl._create_unverified_context()
            headers={'Accept-Charset': 'utf-8', 'Content-Type': 'application/json'}
            req =  urllib.request.Request(url,headers=headers,method='POST')
            res_data = urllib.request.urlopen(req,context=context)
            res = res_data.read()
            jg=json.loads(res.decode("utf8"))
            例外=jg["wddata"]
        except:
            sw3.swexit(1,"获取工作日数据出错")

def lastday(rq,wtype='0'):  #取指定日期的上一工作日
    if len(例外)==0:获取例外数据()
    lastd, xq, jg, i = (None, None, None, 0)
    while i < 30:
        lastd = datetime.datetime.strptime(rq, "%Y%m%d") - datetime.timedelta(days=1)
        rq = lastd.strftime('%Y%m%d')
        xq = lastd.weekday()
        if (xq >= 5 and rq in 例外[wtype]):
            return rq
        if (xq < 5 and rq not in 例外[wtype]):
            return rq
        i = i + 1
    return rq
    
def nextday(rq,wtype='0'):  #取指定日期的下一工作日
    if len(例外)==0:获取例外数据()
    nextd, xq, jg, i = (None, None, None, 0)
    while i < 30:
        nextd = datetime.datetime.strptime(rq, "%Y%m%d") + datetime.timedelta(days=1)
        rq = nextd.strftime('%Y%m%d')
        xq = nextd.weekday()
        if (xq >= 5 and rq in 例外[wtype]):
            return rq
        if (xq < 5 and rq not in 例外[wtype]):
            return rq
        i = i + 1
    return rq

def isworkday(rq,wtype='0'):    #判断是否工作日
    if len(例外)==0:获取例外数据()
    xq=datetime.datetime.strptime(rq, "%Y%m%d").weekday()   #返回0-6,1是周一，6是周日
    if xq<5:    #周一到周五
        return rq not in 例外[wtype]
    else:
        return rq in 例外[wtype]

def nWorkday(rq,n):     # 指定日期rq开始第N个工作日
    if isworkday(rq): n = n - 1
    zxrq = rq
    for i in range(0, n):
        zxrq = nextday(zxrq)
    return zxrq

def 下一天(rq):    #获取下一自然日
    return (datetime.datetime.strptime(rq, "%Y%m%d") + datetime.timedelta(days=1)).strftime('%Y%m%d')

def 上一天(rq):    #获取上一自然日
    return (datetime.datetime.strptime(rq, "%Y%m%d") - datetime.timedelta(days=1)).strftime('%Y%m%d')

是工作日=isworkday
上一工作日=lastday
下一工作日=nextday
