#!/usr/bin/python3
# -*- coding: utf8 -*-

__all__=["读简单配置","获取组成员","未完成退出","异常退出","sw配置文件","c_object"]

import time,base64,sys,json,urllib.request,ssl,os,datetime
import libsw3 as sw3
sw3.__all__=sw3.__all__ + __all__

def 读简单配置(文件名,项目):  #读简单配置文件，一行一条数据，第一列是项目，返回项目后的内容
    dh,_=os.path.splitdrive(os.getcwd())
    fn=os.path.join(dh,"/etc",文件名)
    if os.path.isfile(fn):
        f=open(fn,"r")
    else:
        sw3.swexit(-1,"无法打开连接串配置文件%s" %(fn))
    wjnr=f.readlines()
    f.close()
    for i in wjnr:
        s=i.split()
        if len(s)<2:
            continue
        if s[0]==项目:
            return " ".join(s[1:])
    return ""

def 获取组成员(组id):
    pass

def 未完成退出(信息,*参数):
    if len(参数)>0:
        信息=信息 %(参数)
    sw3.swexit(1,信息)

def 异常退出(信息,*参数):
    if len(参数)>0:
        信息=信息 %(参数)
    sw3.swexit(-1,信息)

def sw配置文件(文件名):    #根据文件名，返回带目录的配置文件名
    dh,_=os.path.splitdrive(os.getcwd())
    return os.path.join(dh,"/etc",文件名)

class c_object(object):
    def __init__(self):
        self.rtcode=0   #返回码
        self.rtinfo=""  #返回信息
        self.ehm=0      #出错处理机制，0不处理，1输出信息，2触发故障
        self.displevel=-1    #显示级别，小于等于这个级别的才会显示
    def q(self,返回码,参数={}):
        self.消息表={
            0:"无错误",
        }
        self.rtcode=返回码
        self.rtinfo=self.消息表.get(返回码,f"未定义的返回码:{返回码}").format(**参数)
        if self.ehm==1:
            print(self.rtinfo)
        if self.ehm==2:
            raise Exception(self.rtinfo)
        return self.rtcode
    def p(self,显示级别,显示消息):
        if 显示级别>self.displevel:return
        print(time.strftime('%Y-%m-%d %H:%M:%S') + f"|{显示级别}|"  + 显示消息)
