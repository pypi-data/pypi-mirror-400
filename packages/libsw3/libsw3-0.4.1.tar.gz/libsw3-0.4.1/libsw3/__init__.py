#!/usr/bin/python3
# -*- coding: utf8 -*-

__all__=["sw3"]

from . import libswn as swn
from .workday import *
from .database import *
from .msgc import *
from .utils import *
from .sendemail import *
from .qiwei import *

import libsw3 as sw3

import datetime,time,inspect,collections,hashlib,base64,urllib.request,json,subprocess
import os,re,shutil,smtplib,sys,getpass
from email import encoders

dqrq12=time.strftime('%Y%m%d',time.localtime(time.time()-12*3600))
dqrq=time.strftime("%Y%m%d")

def appmonitor(appname):
    url="http://xtjk.rt/appmonitor.fcgi?app=%s" %(appname)
    req =  urllib.request.Request(url,method='GET')
    res_data = urllib.request.urlopen(req)
    res = res_data.read()

def cpt(t):
    import json
    print(json.dumps(t,ensure_ascii=False,skipkeys=False,indent=2))

def crun(cmd,errquit=True):
    p(3,"执行命令: %s",cmd)
    fhm=os.system(cmd)
    if fhm!=0 and errquit:
        mn=sys.argv[0].split("/")[-1]
        p(0,"执行命令%s返回值为%d，出错退出" %(cmd,fhm))
        sys.exit(1)

def prun(cmd,errquit=True): #执行命令并输出结果
    p(3,"执行命令: %s",cmd)
    pp=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    outstd,outerr=pp.communicate()
    if pp.returncode==0:
        if outstd:
            p(1,outstd.decode())
        if outerr:
            p(1,outerr.decode())
    else:
        info="执行出错，返回码%d\n" %(pp.returncode)
        if outstd:info=info+"%s\n" %(outstd.decode())
        if outerr:info=info+"%s\n" %(outerr.decode())
        if errquit:
            swexit(-1,info)
        else:
            p(1,info)

def filemtime(wj):
    if not os.path.isfile(wj):
        return 0
    return os.stat(wj).st_mtime

def getparam(pname):
    if len(sys.argv)<3: return None
    for i in range(2,len(sys.argv)):
        jg = re.search("=", sys.argv[i])
        if sys.argv[i][0:jg.span()[0]] == pname:
            return sys.argv[i][jg.span()[1]:]
    return None

def getarg(*args,**kwargs):
    jg=[]
    for i in range(len(args)):
        x=args[i]
        if len(sys.argv)>i+2:
            if type(args[i])==int:
                x=int(sys.argv[i+2])
            if type(args[i])==float:
                x=float(sys.argv[i+2])
            if type(args[i])==str:
                x=sys.argv[i+2]
            if type(args[i])==bool:
                if sys.argv[i+2].lower() in ["yes","1","true"]:
                    x=True
                if sys.argv[i+2].lower() in ["no","0","false"]:
                    x=False
        jg.append(x)
    if len(jg)==1:
        return jg[0]
    return jg

def makedirs(d):
    if not os.path.isdir(d):
        os.makedirs(d)

def mkdir(d):
    if not os.path.isdir(d):
        os.mkdir(d)

def sendok(dirorfile,targetdir="",ext=".ok"):#发送文件或者目录下所有文件到目标目录，并附加.ok文件 新版本，targetdir如果为""，就不再拷贝，直接生成ok文件并发送
    if type(targetdir)!=type(""):
        return
    if type(dirorfile)!=type(""):
        return
    if targetdir[-1:]=="/":
        targetdir=targetdir[:-1]
    if dirorfile[-1:]=="/":
        dirorfile=dirorfile[:-1]
    if not os.path.isdir(targetdir) and targetdir!="":
        return
    if os.path.isfile(dirorfile):
        if targetdir=="":
            fok=dirorfile+ext
        else:
            fok="%s/%s%s" %(targetdir,dirorfile.split("/")[-1],ext)
        fok1=fok+"1"
        if targetdir!="":
            shutil.copy2(dirorfile,targetdir)
        os.system("touch %s" %(fok1))
        if os.stat(dirorfile).st_mtime>os.stat(fok1).st_mtime-2:
            os.utime(fok1,(os.stat(dirorfile).st_mtime+60,os.stat(dirorfile).st_mtime+60))
        shutil.move(fok1,fok)
    elif os.path.isdir(dirorfile):
        for fn in os.listdir(dirorfile):
            sendok(dirorfile+"/"+fn,targetdir,ext)

def unlink(fn):
    if os.path.isfile(fn):
        os.unlink(fn)

def zipfileisok(wj):    #测试zip文件是否正常，为真表示没问题
    if not os.path.isfile(wj):
        return False
    if os.system("unzip -qqt %s" %(wj))!=0:
        return False
    return True

class c_commandarg: #根据命令行参数调用模块及显示相应help
    tcmd={}
    scriptname=""
    def __init__(self,gg,scriptname):
        c_commandarg.scriptname=scriptname
        for g in gg:
            if (inspect.isfunction(gg[g]) or inspect.isclass(gg[g])) and gg[g].__doc__!=None:
                c_commandarg.tcmd[g]=gg[g]
    def main(self):
        if len(sys.argv)>1:
            cmd=sys.argv[1]
        elif "main" in c_commandarg.tcmd:
            cmd="main"
        else:
            self.printhelp()
            return
        if cmd not in c_commandarg.tcmd:
            self.printhelp()
            print("-------------------------")
            swexit(sys._getframe().f_lineno,"%s 命令没找到！" %(cmd))
        cf=c_commandarg.tcmd[cmd]
        if inspect.isfunction(cf):
            rtn=cf()
        else:
            c=cf()
            rtn=0
            if hasattr(c,"main"):
                rtn=c.main()
        return rtn
    
    @staticmethod
    def printhelp():
        '''显示程序说明及命令行、参数信息'''
        print(c_commandarg.scriptname)
        print("-"*len(c_commandarg.scriptname)*2)
        maxcmdsize=0
        scmd=[]
        for name in c_commandarg.tcmd:
            scmd.append(name)
            if len(name)>maxcmdsize:
                maxcmdsize=len(name)
        scmd.sort()
        for name in scmd:
            print("%-*s   %s" %(maxcmdsize,name,c_commandarg.tcmd[name].__doc__))

def redp(s):
    print("\x1b[0;31;40m%s\x1b[0m" %(s))

def base64encode(filename): #获取文件的base64编码
    if not os.path.isfile(filename):return ""
    m = hashlib.md5()
    with open(filename,'rb') as f:
        s64=base64.b64encode(f.read())
    return s64

def filemd5(filename):#获取文件的md5值
    if not os.path.isfile(filename):return ""
    m = hashlib.md5()
    with open(filename,'rb') as f:
        m.update(f.read())
    return m.hexdigest()

def onlyone():  #实例仅运行一次，如果有多于1个则退出运行
    if len(sys.argv)<2:return
    jg=os.popen("ps ax").read()
    搜索串=f"python\S*\s+\S*{sys.argv[0]}\s+{sys.argv[1]}"
    sj=re.findall(搜索串,jg)
    搜索串2=f"python\S*\s+\S*{sys.argv[0]}\s+{sys.argv[1]}\S+"
    sj2=re.findall(搜索串2,jg)
    if len(sj)-len(sj2)>1:
        异常退出("有多于一个的实例，退出\n")

class taora(c_oracle):
    def __init__(self,ta="hsta",changeable=False):
        self.ta=ta
        if self.ta in ["hsta","hbetf","lofta","bjhg2"]:
            self.sora="%s@ta" %(self.ta)
            ta自身=c_oracle(self.sora)
            ta自身.importdbdriver()
            ta自身.解析连接参数()
            oraconn = ta自身.连接参数1[0]
            if oraconn == "":
                swexit(-1,"数据库配置文件中未找到%s@ta配置" % (self.ta))
            self.realuser=oraconn.split("/")[0]#用于自动转换
            if not changeable:
                self.sora = "taro2@ta"
        else:
            swexit(-1,"数据库请求参数有误，只读数据库参数应为：hsta、hbetf、lofta、bjhg、bjhg2之一")
        super().__init__(self.sora)
    def convuser(self,ssql):    #根据ta和实际连接的用户把sql中的 " hsta."等转化为 " ta4t1."等，用于无缝对接生产和测试
        return ssql.replace(" %s." %(self.ta)," %s." %(self.realuser))
    def execute(self,ssql,*args,**kwargs):
        return super().execute(self.convuser(ssql),*args,**kwargs)
    def flowlog(self,fn):   #检查当前流程是否已经跑完，流程可以用id或者名称
        if type(fn)==int:
            if self.ta in ["bjhg2"]:
                return self.jg1("select c_dealflag from %s.ttaflow where l_id=%d" %(self.ta,fn))=="9"
            else:
                return self.jg1("select c_dealflag from %s.ttaflowlog where l_id=%d" %(self.ta,fn))=="1"
        if type(fn)==str:
            if self.ta in ["bjhg2"]:
                return self.jg1("select c_dealflag from %s.ttaflow where c_flowcode like '%s%%' or c_flowname like '%s%%'" %(self.ta,fn,fn))=="9"
            else:
                return self.jg1("select c_dealflag from %s.ttaflowlog where c_flowcode like '%s%%' or c_flowname like '%s%%'" %(self.ta,fn,fn))=="1"
        return False
    def isworkday(self,rq):
        if self.ta in ["hsta"]:
            return self.jg1("select l_workflag from %s.topenday where d_date='%s' and c_fundcode='******' and c_agencyno='***'" %(self.ta,rq))==1
        elif self.ta in ["bjhg2"]:
            weekd = datetime.datetime.strptime(rq, '%Y%m%d').weekday()
            jg = self.jg1("select count(*) from %s.tworkday where d_date='%s' and c_type='0'" %(self.ta,rq))
            if (weekd >= 5 and jg==1):
                return True
            if (weekd < 5 and jg==0):
                return True
            return False
        else:
            return self.jg1("select l_workflag from %s.topenday where to_char(d_date,'yyyymmdd')='%s'" %(self.ta,rq))==1
    def jg1(self,ssql,**kwargs):
        return super().jg1(self.convuser(ssql),**kwargs)
    def lastday(self,rq):   #取指定日期的上一工作日
        if self.ta in ["hsta"]:
            return self.jg1("select max(d_date) from %s.topenday where l_workflag=1 and d_date<'%s'" %(self.ta,rq))
        elif self.ta in ["bjhg2"]:
            lastd, xq, jg, i = (None,None,None,0)
            while i<30:
                lastd = datetime.datetime.strptime(rq, "%Y%m%d") + datetime.timedelta(days=-1)
                xq = lastd.weekday()
                jg = self.jg1("select count(*) from %s.tworkday where d_date='%s' and c_type='0'" % (self.ta,lastd.strftime('%Y%m%d')))
                if (xq >= 5 and jg==1):
                    break
                if (xq < 5 and jg==0):
                    break
                rq = lastd.strftime('%Y%m%d')
                i = i + 1
            return lastd.strftime('%Y%m%d')
        else:
            return self.jg1("select to_char(max(d_date),'yyyymmdd') from %s.topenday where l_workflag=1 and to_char(d_date,'yyyymmdd')<'%s'" %(self.ta,rq))
    def nextday(self,rq):   #取指定日期的下一工作日
        if self.ta in ["hsta"]:
            return self.jg1("select min(d_date) from %s.topenday where l_workflag=1 and d_date>'%s'" %(self.ta,rq))
        elif self.ta in ['bjhg2']:
            nextd, xq, jg, i = (None,None,None,0)
            while i<30:
                nextd = datetime.datetime.strptime(rq,"%Y%m%d") + datetime.timedelta(days=1)
                xq = nextd.weekday()
                jg = self.jg1("select count(*) from %s.tworkday where d_date='%s' and c_type='0'" %(self.ta,nextd.strftime('%Y%m%d')))
                if (xq >= 5 and jg==1):
                    break
                if (xq < 5 and jg==0):
                    break
                rq = nextd.strftime('%Y%m%d')
                i = i + 1
            return nextd.strftime('%Y%m%d')
        else:
            return self.jg1("select to_char(min(d_date),'yyyymmdd') from %s.topenday where l_workflag=1 and to_char(d_date,'yyyymmdd')>'%s'" %(self.ta,rq))
    def sysdate(self):  #取当前系统日期
        if self.ta in ["bjhg2"]:
            return self.jg1("select c_value from %s.tsysparameter where c_item='sysdate' and c_class='bjhg'" %(self.ta))
        else:
            return self.jg1("select c_value from %s.tsysparameter where c_ITEM='SysDate' and c_class='System'" %(self.ta))
    def xg(self,ssql,**kwargs):
        return super().xg(self.convuser(ssql),**kwargs)

class c_kfjjjk(object):#开放基金交换文件接口的处理
    def __init__(self,ml="",sywj=""):
        if ml!="" and sywj!="":
            self.ml=ml
            self.sywj=sywj
    def copy(self,mbml):    #拷贝所有文件到目标目录
        for wj in self.sjwj:
            shutil.copy2(wj,mbml)
    def jc(self):   #检查，为真表示检查失败
        self.sjwj=[]    #数据文件
        sy="%s/%s" %(self.ml,self.sywj)
        self.sjwj.append(sy)
        if not os.path.isfile(sy):
            return "索引文件 %s 未找到" %(sy)
        if self.jcwjw(sy):
            return "索引文件 %s 未找到文件尾：OFDCFEND" %(sy)
        with open(sy) as f:
            synr=f.readlines()  #读入索引文件内容
        if len(synr)<8:
            return "索引文件 %s 格式错误或者没有接收完全" %(sy)
        try:
            wjsl=int(synr[5])
        except:
            return "索引文件 %s 格式错误，数据文件数量不对" %(sy)
        if len(synr)<wjsl+7:
            return "索引文件 %s 格式错误或者没有接收完全" %(sy)
        for wjmc in synr[6:wjsl+6]:
            sjwj="%s/%s" %(self.ml,wjmc.strip())
            if self.jcwjw(sjwj):
                return "数据文件 %s 格式错误或者没有接收完全" %(sjwj)
            self.sjwj.append(sjwj)
        return False
    def jcwjw(self,wjm):    #检查文件尾是否有OFDCFEND，为真表示有问题
        if not os.path.isfile(wjm):
            return True
        with open(wjm,encoding="gbk",errors='ignore') as f:
            for a in f:
                b=a.strip()
                if b=="OFDCFEND":
                    return False
        return True
    def move(self,mbml):    #移动所有文件到目标目录
        for wj in self.sjwj:
            shutil.move(wj,mbml)

def p(level,fmt,*info):#输出信息
    if not oraconn:return swn.p(level,fmt,*info)
    global logno
    try:
        if level>loglevel and level!=-1:return  #级别较低不输出,-1是错误输出，输出到标准错误上
        if info is None or not info:
            sinfo = time.strftime('%Y-%m-%d %H:%M:%S') + "|%d|" % (level) + fmt
        else:
            sinfo=time.strftime('%Y-%m-%d %H:%M:%S')+"|%d|" %(level) +fmt %(info)
        if level>=0:
            print(sinfo)
        else:
            sys.stderr.write(sinfo+"\n")
        if not swdb.connected:return    #事务数据库没联上，不输出数据库日志
        if swid==0 or logid==0:return   #事务id或者调用id为0则返回
        insertSql = "insert into sw_detaillog (dispathno,swid,no,log_time,log_msg,log_level) values (:dispathno,:swid,:no,sysdate,:log_msg,:log_level)"
        cur = swdb.conn.cursor()
        cur.setinputsizes(log_msg=swdb.dbdriver.BLOB)
        cur.execute(insertSql, {'dispathno':logid,'swid':swid,'no':logno,'log_msg':sinfo.encode("gbk"),'log_level':level})
        logno = logno + 1
        swdb.conn.commit()
    except:
        print("日志打印异常")

def sjbj(sjhm,nr,td="AB"):  #手机报警
    if type(sjhm)==type('str'):
        sjhm=[sjhm]
    cc=c_oracle("xtjk@cc")
    for hm in sjhm:
        cc.jg1("select smsalert(:hm,:nr,4,:td) from dual",hm=hm,nr=nr,td=td)

def swexit(returncode,msg="",nextchecktime=""): #事务退出环节
    global swrq
    if swid==0: #事务id为0是测试，不用写退出环节
        if msg:p(1,msg)
        sys.exit(returncode)
    if not oraconn:return swn.exit(returncode,msg,nextchecktime)
    usetime = time.time()-stime
    stime_fmt = time.strftime("%Y%m%d%H%M%S",time.localtime(stime))
    if returncode==0:   #返回码为0，正常退出
        rqlx,kssj,jcsj=swdb.jg1("select datetype,stime,to_char(sysdate+interval/3600/24,'yyyymmddhh24miss') from sw where id=:swid",swid=swid)
        if rqlx==1: #日期类型为1，按工作日
            swrq=nextday(swrq)
            jcsj="%s%s00" %(swrq,kssj)  #下次检查时间
        if rqlx==2: #日期类型为2，按自然日
            swrq=(datetime.datetime.strptime(swrq, "%Y%m%d") + datetime.timedelta(days=1)).strftime("%Y%m%d")
            jcsj="%s%s00" %(swrq,kssj)  #下次检查时间
        if rqlx==3: #日期类型为3，不按日期
            swrq=dqrq
        swdb.execute("update sw set rtncode=0,rtnmsg='',locker='',nextcheck=to_date(:jcsj,'yyyymmddhh24miss'),swrq=:swrq,status=swtype where id=:swid",swid=swid,swrq=swrq,jcsj=jcsj)
    elif returncode<0:  #返回码为负，异常退出
        swdb.execute("update sw set rtncode=:rtcode,rtnmsg=:rtmsg,locker='',status=2 where id=:swid",rtcode=returncode,rtmsg=msg,swid=swid)
    else:   #返回码为正，多半是条件不满足
        if nextchecktime:
            swdb.execute("update sw set rtncode=:rtcode,rtnmsg=:rtmsg,locker='',nextcheck=to_date(:nextchecktime,'yyyymmddhh24miss') where id=:swid",rtcode=returncode,rtmsg=msg,swid=swid,nextchecktime=nextchecktime)
        else:
            swdb.execute("update sw set rtncode=:rtcode,rtnmsg=:rtmsg,locker='',nextcheck=sysdate+interval/3600/24 where id=:swid",rtcode=returncode,rtmsg=msg,swid=swid)
    swdb.execute("update sw_dispath set use_time=(sysdate-dispath_time)*24*3600 where dispathno=:dispathno and swid=:swid",dispathno=logid,swid=swid)
    swdb.commit()
    sys.exit(returncode)

def swenv(envname,dftval):  #根据默认值自动调用swenvs或者swenvi
    prefix=os.environ.get("envprefix","sw3")
    if type(dftval)==type(""):
        return os.environ.get("%s_%s" %(prefix,envname),dftval)
    s=os.environ.get("%s_%s" %(prefix,envname),"%d" %(dftval))
    try:
        i=int(s)
    except:
        return dftval
    return i

def start(gg,scriptname):   #启动
    swn.sw3=gg.get("sw3",{})
    onlyone()
    c=c_commandarg(gg,scriptname)
    c.main()
    swexit(0)

def swok():
    '''直接置事务正常完成'''
    swexit(0)

stime=time.time()
logno=1
swdb=c_oracle()
swid=swenv("swid",0)
logid=swenv("logid",0)
loglevel=swenv("loglevel",5)
swrq=swenv("swrq",dqrq)
oraconn=swenv("oracle","")
if oraconn!="":
    swdb.connect(oraconn)
else:
    swdb=None
srvname=swenv("srvname","")
srvpass=swenv("srvpass","")
xx=c_xx()
xxtz=c_xxtz()
istest=(swenv("istest","")!="")
testmail=swenv("testmail","")

if __name__ == "__main__":
    start(globals(),"libsw3库")
