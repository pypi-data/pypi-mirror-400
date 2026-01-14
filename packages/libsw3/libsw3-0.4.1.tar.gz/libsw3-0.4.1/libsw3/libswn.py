#!/usr/bin/python3
# -*- coding: utf8 -*-

import libsw3 as sw3
import time,base64,sys,json,urllib.request,ssl,os

version="libswn_1"
saveinfo=[]

class webapi(object):
    def detaillog(self,level,msg):
        self.sj={}
        self.sj["name"]=sw3.srvname
        self.sj["password"]=sw3.srvpass
        self.sj["taskid"]=sw3.swid
        self.sj["dispathno"]=sw3.logid
        self.sj["no"]=sw3.logno
        self.sj["level"]=level
        self.sj["msg"]=base64.b64encode(msg[:2000].encode("utf8")).decode("utf8")
        return self.get("detaillog")

    def updatesw(self,returncode,msg,nextchecktime):
        self.sj={}
        self.sj["name"]=sw3.srvname
        self.sj["password"]=sw3.srvpass
        self.sj["taskid"]=sw3.swid
        self.sj["rtncode"]=returncode
        self.sj["rtnmsg"]=base64.b64encode(msg[:2000].encode("utf8")).decode("utf8")
        return self.get("updatesw")

    def get(self,method):  #获取数据
        url="https://swnweb.rt/api?method="+method
        try:
            context = ssl._create_unverified_context()
            data=json.dumps(self.sj,ensure_ascii=False,skipkeys=False).encode("utf8")
            headers={'Accept-Charset': 'utf-8', 'Content-Type': 'application/json'}
            req =  urllib.request.Request(url,data=data,headers=headers,method='POST')
            res_data = urllib.request.urlopen(req,context=context)
            res = res_data.read()
            jg=json.loads(res.decode("utf8"))
        except:
            jg={"code":-1,"err":"访问 %s 时故障" % url}
        return jg

def exit(returncode,msg,nextchecktime):  #退出函数
    usetime = time.time()-sw3.stime
    stime_fmt = time.strftime("%Y%m%d%H%M%S",time.localtime(sw3.stime))
    api=webapi()
    for info in saveinfo:
        while True:
            api.sj=info
            jg=api.get("detaillog")
            if jg["code"]==0:break
            time.sleep(5)
    while True:
        jg=api.updatesw(returncode,msg,nextchecktime)
        if jg["code"]==0:break
        time.sleep(5)
    os.system("touch /var/spool/sw3/%s.ok" %(sw3.swid))
    sys.exit(returncode)

def p(level,fmt,*info):#输出信息
    if level>sw3.loglevel and level!=-1:return  #级别较低不输出,-1是错误输出，输出到标准错误上
    if info is None or not info:
        sinfo = time.strftime('%Y-%m-%d %H:%M:%S') + "|%d|" % (level) + fmt
    else:
        try:
            sinfo=time.strftime('%Y-%m-%d %H:%M:%S')+"|%d|" %(level) +fmt %(info)
        except:
            sinfo= time.strftime('%Y-%m-%d %H:%M:%S') + "|%d|" % (level) + fmt
    if level>=0:
        print(sinfo)
    else:
        sys.stderr.write(sinfo+"\n")
    if sw3.logid==0:return
    api=webapi()
    jg=api.detaillog(level,sinfo)
    if jg["code"]!=0:
        saveinfo.append(api.sj)
    sw3.logno=sw3.logno+1
