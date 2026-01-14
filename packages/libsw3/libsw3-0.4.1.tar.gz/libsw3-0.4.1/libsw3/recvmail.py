#!/usr/bin/python3
# -*- coding: utf8 -*-

import datetime
import re
import smtplib
import os
import sys
import shutil
import time
import poplib
import email
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
import base64
import types
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import exchangelib

__all__=["c_recvpop3","c_recvexchange"]

from .utils import *

def 读ini(ini文件名):
    import configparser
    cfg = configparser.ConfigParser()
    dh,_=os.path.splitdrive(os.getcwd())
    cfg.read(sw配置文件(ini文件名))
    return cfg

class c_recvpop3(c_object):  #使用pop3接收邮件，当前只处理附件
    def recvmail(self,参数):   #接收邮件，参数是swmail.cfg中的某节的数据
        cfg=读ini("swmail.cfg")
        self.mailaddr=cfg[参数]["user"]
        self.mailpass=cfg[参数]["password"]
        self.mailserver=cfg[参数]["recvserver"]
        p=poplib.POP3(self.mailserver)  #联接邮件服务器
        self.p(2,p.getwelcome().decode())
        p.user(self.mailaddr)   #向服务器输出用户名
        p.pass_(self.mailpass)  #向服务器输出密码
        self.p(2,"messages: %s. size: %s" % p.stat())  #邮件数量，总大小
        resp,mails,octets=p.list()
        js=len(mails)
        idx=js+1
        while idx>1:    #从最新的邮件开始
            idx=idx-1
            data={"uid":p.uidl(idx).split()[2],"idx":idx} #邮件的id号，用来跳过接收出错的邮件
            self.p(3,f"序号：{idx} uid:{data['uid']}")
            try:
                resp,lines,octets=p.top(idx,0)
            except:
                print("接收%d邮件头出错,uid=%s" %(idx,self.uid))
                continue
            msg_content=""
            for msg in lines:
                msg_content=msg_content + msg.decode() + "\r\n"
            self.getsender(msg_content,data) #解析得到发件人等信息
            data["date"]=self.readmaildate(msg_content) #解析文件日期
            if self.handle_head(data):  #读入文件头之后的处理
                continue
            self.handle_delmail()   #处理删除邮件，默认并不删除
            try:
                resp,lines,octets=p.retr(idx)
            except:
                print("接收%d邮件正文出错,uid=%s" %(idx,self.uid))
                continue
            msg_content=""
            for msg in lines:
                msg_content=msg_content + msg.decode() + "\r\n"
            msg=Parser().parsestr(msg_content)
            for part in msg.walk():
                filename=part.get_filename()
                if filename==None:
                    continue
                filename=self.decode_filename(filename)
                try:
                    self.attfile=filename.encode("gbk")
                except:
                    self.attfile=""
                self.attfile=filename
                self.savename=""
                self.handle_bf_attfile(data)    #处理附件之前
                if self.savename:
                    f=open(self.savename,"wb")
                    f.write(base64.b64decode(part.get_payload()))
                    f.close()
                    self.handle_af_attfile(data)    #处理附件之后
        p.quit()
    def decode_filename(self,fn):
        for value,charset in decode_header(fn):
            if charset:
                try:
                    value = value.decode(charset)
                except:
                    value=""
            return value
    def decode_str(self,s):
        jg=[]
        for value,charset in decode_header(s):
            if charset:
                if charset=="gb2312":charset="gbk"
                try:
                    value = value.decode(charset)
                except:
                    print("解析 %s:%s出错！" %(value,charset))
            jg.append(value)
        return jg
    def getsender(self,msg_content,data):#邮件解析，返回发送者
        msg=Parser().parsestr(msg_content)
        data["subject"]=self.jmt(msg,"Subject")[0]  #标题
        data["sendername"],data["sender"]=self.jmt(msg,"From")     #发件人名称，发件人地址
    def handle_af_attfile(self,data):    #处理附件之后
        self.p(2,"handle_af_attfile:{data}")
    def handle_bf_attfile(self,data):    #处理附件之前
        self.p(2,f"handle_bf_attfile:{data}")
        self.p(2,"在这个函数里设置self.savename则将附件保存")
    def handle_delmail(self):   #处理删除邮件，默认并不删除
        if not hasattr(self,"deloldmail"):return
        if (datetime.date.today()-datetime.timedelta(days=self.deloldmail)).strftime("%Y%m%d")>self.maildate:
            print("邮件时间较长，删除")
#			p.dele(idx)
    def handle_head(self,data):  #读入邮件头之后的处理
        self.p(2,f"handle_head:{data}")
    def jmt(self,msg,xm):   #解码文件头，xm为 From To Subject
        value = msg.get(xm,"")
        if value:
            if xm=="Subject":
                jg=self.decode_str(value)
                if len(jg)==0:
                    jg=""
                return jg
            else:
                hdr,addr=parseaddr(value)
                name=self.decode_str(hdr)
                return name[0],addr
        return "",""
    def readmaildate(self,msg_content): #返回邮件日期
        msg=Parser().parsestr(msg_content)
        rq=email.utils.parsedate(msg.get("Date"))
        if rq==None:
            return "20991231"
        return "%s%02d%02d" %(rq[0],rq[1],rq[2])

class c_recvexchange(object):    #接收微软exchange服务器邮件，当前只接收附件
    def recvmail(self,参数):   #接收邮件，参数是swmail.cfg中的某节的数据
        cfg=读ini("swmail.cfg")
        self.mailaddr=cfg[参数]["user"]
        self.mailpass=cfg[参数]["password"]
        self.mailserver=cfg[参数]["recvserver"]
        exchangelib.protocol.BaseProtocol.HTTP_ADAPTER_CLS = exchangelib.protocol.NoVerifyHTTPAdapter
        credentials = exchangelib.Credentials(self.mailaddr,self.mailpass)
        config = exchangelib.Configuration(server=self.mailserver, credentials=credentials,auth_type=exchangelib.NTLM)
        account = exchangelib.Account(self.mailaddr, credentials=credentials, autodiscover=False,config=config)
        for item in account.inbox.all().order_by('-datetime_received'):
            data={"sender":item.sender.email_address}
            data["date"]=item.datetime_received.strftime('%Y%m%d')
            data["subject"]=item.subject
            if self.handle_delmail(data):
                item.delete()
            if self.handle_head(data):  #读入文件头之后的处理
                continue
            for attachment in item.attachments:
                data["attfile"]=attachment.name
                self.savename=""
                self.handle_bf_attfile(data)    #处理附件之前
                if self.savename:
                    f=open(self.savename,"wb")
                    f.write(attachment.content)
                    f.close()
                    self.handle_af_attfile(data)    #处理附件之后
    def handle_af_attfile(self,data):    #处理附件之后
        pass
    def handle_bf_attfile(self,data):    #处理附件之前
        pass
    def handle_delmail(self,data):   #处理删除邮件，默认并不删除
        if not hasattr(self,"deloldmail"):return False
        deldate=(datetime.date.today()-datetime.timedelta(days=self.deloldmail)).strftime("%Y%m%d")
        if deldate>data['date']:
            return True
        else:
            return False
    def handle_head(self,data):  #读入邮件头之后的处理
        pass
