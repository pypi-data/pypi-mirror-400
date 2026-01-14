#!/usr/bin/python3
# -*- coding: utf8 -*-

from libsw3 import *
import os,getpass,json,urllib,hashlib,base64,sys

class 代码管理(object):
    def __init__(self):
        prefix=os.environ.get("envprefix","sw3")
        self.server=sw3.swenv("server","sw3.rt")
        user=sw3.swenv("user","")
        if user=="":
            user=input("输入确认身份用的用户名:")
        passwd=sw3.swenv("passwd","")
        if passwd=="":
            passwd=getpass.getpass("未能在环境变量中获取密码，需要手工输入%s的密码:" %(user))
        self.sj={}
        self.sj["pubLevel"]="0"
        self.sj["updateBy"]=user
        self.sj["passwd"]=passwd
    def up(self,fn):#上传文件
        self.url="http://%s/swapi/updateProgram" %(self.server)
        self.sj["md5"]=sw3.filemd5(fn)
        self.sj["script"]=sw3.base64encode(fn).decode("utf8")
        self.sj["svcname"]=fn.split("/")[-1]
        print(fn,end="   ")
        jg=self.get()
        if jg["code"]==0:
            print("上传成功")
    def down(self,fn):#下载文件
        self.url="http://%s/swapi/programInfo" %(self.server)
        self.sj["svcname"]=fn.split("/")[-1]
        return self.get()
    def get(self):  #获取数据
        data=json.dumps(self.sj,ensure_ascii=False,skipkeys=False).encode("utf8")
        headers={'Accept-Charset': 'utf-8', 'Content-Type': 'application/json'}
        req =  urllib.request.Request(self.url,data=data,headers=headers,method='POST')
        res_data = urllib.request.urlopen(req)
        res = res_data.read()
        jg=json.loads(res.decode("utf8"))
        if jg["code"]==404:
            print("服务器不存在此脚本")
        elif jg["code"]!=0:
            print(jg)
        return jg

def install():
    '''更新脚本到服务器，参数可指定要发布的文件，不指定则发布自己'''
    fn=sw3.getarg(sys.argv[0])
    api=代码管理()
    if not os.path.exists(fn):
        sw3.swexit(1,"未找到指定的文件%s" %(fn))
    if os.path.isfile(fn):
        api.up(fn)
    else:
        for f in os.listdir(fn):
            api.up("%s/%s" %(fn,f))

class cks(object):
    '''检查脚本和服务器上的脚本的差异，可指定脚本名称，不指定则检查目录下所有文件'''
    def __init__(self):
        fn=sw3.getarg(".")
        self.api=代码管理()
        if not os.path.exists(fn):
            sw3.swexit(1,"未找到指定的文件%s" %(fn))
        if os.path.isfile(fn):
            self.ck(fn)
        else:
            for f in os.listdir(fn):
                self.ck("%s/%s" %(fn,f))
    def ck(self,f):
        import difflib
        if os.path.isdir(f):return
        print(f,end="  ")
        jg=self.api.down(f)
        if jg["code"]==0:
            data=jg["data"]
            localmd5=sw3.filemd5(f)
            if data["md5"]==localmd5:
                print("")
            else:
                print("文件md5:%s 数据库中文件md5:%s" %(localmd5,data["md5"]))
                if f.endswith("py"):
                    diff=difflib.Differ()
                    n1=base64.b64decode(data["script"]).decode("utf8")
                    with open(f,"rb") as f:
                        n2=f.read().decode("utf8")
                    #print("\n".join(diff.compare(n1.split("\n"),n2.split("\n"))))
                    print("\n".join(difflib.context_diff(n1.split("\n"),n2.split("\n"))))

def convdbconf():
    '''转换数据库配置文件'''
    老配置文件=sw配置文件("oraconn.cfg")
    if not os.path.isfile(老配置文件):
        未完成退出("没找到 %s 文件",老配置文件)
    f=open(老配置文件)
    wjnr=f.readlines()
    f.close()
    模板=[
        {
                "db":"oracle",
                "t":[],
                "d":{
                }
        }
]
    新配置目录=sw配置文件("dbconn.config.d")
    sw3.makedirs(新配置目录)
    for i in wjnr:
        if i.startswith("#"):
            continue
        s=i.split()
        if len(s)!=2:
            sw3.p(1,"格式错误:%s",i)
            continue
        s1,s2=s
        模板[0]["t"]=[s2]
        配置文件=os.path.join(新配置目录,"%s.cfg" %(s1))
        print(配置文件)
        if os.path.exists(配置文件):
            异常退出("配置文件 %s 已经存在！",配置文件)
        f=open(配置文件,"w")
        f.write(json.dumps(模板,indent=4))
        f.close()

def main():
    sw3.start(globals(),"事务3辅助工具")
