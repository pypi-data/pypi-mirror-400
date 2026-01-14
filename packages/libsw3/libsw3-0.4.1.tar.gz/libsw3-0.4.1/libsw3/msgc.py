#!/usr/bin/python3
# -*- coding: utf8 -*-

__all__ = ["c_xxtz","c_xx"]

import time,sys
import libsw3 as sw3

class c_xxtz(object):
    def __init__(self):
        self.db = sw3.c_oracle("sw3msg@cc")
    def send(self, title="", content="", receiveGroup=None, noticeType="1", noticeTime=None, responseModel="2",saveDay=30):
        '''
        消息通知
        :param title: 标题，对于包含邮件通知方式的请求，标题为必录项
        :param content: 内容，必录项
        :param receiveGroup: 接收人组，多个组通过英文分隔符;分隔。例子：888;999
        :param noticeType: 通知方式，0-短信 1-微信 2-邮箱。同时多种通知方式通过英文分隔符;分隔。例子：0;1;2
        :param noticeTime: 通知发布时间。默认即时发布，可指定发布时间。格式：yyyymmddHHMMSS
        :param responseModel: 通知响应模式：0-所有人必须响应 1-任意一人响应即可 2-不需要响应
        :param saveDay: 通知保留天数，默认30天
        :return:
        '''
        if noticeType is None:
            return False
        if noticeType.find("2") >= 0 and (title is None or title == ""):
            return False
        if content is None or content == "":
            return False
        if receiveGroup is None or receiveGroup == "":
            return False
        if noticeTime is None:
            noticeTime = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        if responseModel is None:
            responseModel = "2"
        requestId = self.db.jg1("select msgc.notice_seq.nextval from dual")
        insertSQL = "insert into msgc.t_notice_request (id,title,content,notice_type,notice_time,model,create_time,create_by,save_days) values (:1,:2,:3,:4,:5,:6,sysdate,0,:7)"
        self.db.execute(insertSQL, {'1': requestId, '2': title, '3': content, '4': noticeType, '5': noticeTime, '6': responseModel, '7': saveDay})
        for groupId in receiveGroup.split(";"):
            if groupId.isdigit():
                self.db.execute("insert into msgc.t_notice_group (notice_id, group_id) values (:1, :2)",{'1': requestId, '2': groupId})
        self.db.commit()
        return True

class c_xx(object):   #消息处理
    def __init__(self):
        self.cc=sw3.c_oracle("sw3msg@cc",yslj=True)
    def dwx(self,组,消息内容,标题=None,消息保存天数=30,栏目=''):
        for 组id in self.组解析(组):
            self.dx(组id,消息内容,标题,消息保存天数)
            self.wx(组id,消息内容,标题,消息保存天数,栏目)
    def dx(self,组,消息内容,标题=None,消息保存天数=30):
        s=sys._getframe(1)
        标题=标题 or "%s:%d" %(s.f_code.co_filename.split("/")[-1] , s.f_lineno)
        for 组id in self.组解析(组):
            self.cc.execute("select f_dx(:z,:xxnr,:bt,:ts) from dual",z=组id,xxnr=消息内容,bt=标题,ts=消息保存天数)
    def gzt(self,组,消息标识,消息内容,标题=None,消息保存天数=30): #工作台消息
        s=sys._getframe(1)
        标题=标题 or "%s:%d" %(s.f_code.co_filename.split("/")[-1] , s.f_lineno)
        if 消息内容=="":消息内容="正常"
        for 组id in self.组解析(组):
            self.cc.execute("select f_gzt(:z,:xxnr,:bt,:ts) from dual",z=组id,xxnr="%s|1|%s" %(消息标识,消息内容),bt=标题,ts=消息保存天数)
    def wx(self,组,消息内容,标题=None,消息保存天数=30,栏目=''):
        s=sys._getframe(1)
        标题=标题 or "%s:%d" %(s.f_code.co_filename.split("/")[-1] , s.f_lineno)
        for 组id in self.组解析(组):
            self.cc.execute("select f_wx(:z,:xxnr,:bt,:ts,:lm) from dual",z=组id,xxnr=消息内容,bt=标题,ts=消息保存天数,lm=栏目)
    def yybb(self,组,消息内容,标题=None,消息保存天数=30):
        s=sys._getframe(1)
        标题=标题 or "%s:%d" %(s.f_code.co_filename.split("/")[-1] , s.f_lineno)
        for 组id in self.组解析(组):
            self.cc.execute("select f_yybb(:z,:xxnr,:bt,:ts) from dual",z=组id,xxnr=消息内容,bt=标题,ts=消息保存天数)
    def mail(self,组,消息内容,标题=None,消息保存天数=30):
        s=sys._getframe(1)
        标题=标题 or "%s:%d" %(s.f_code.co_filename.split("/")[-1] , s.f_lineno)
        消息内容=消息内容.replace("\n","<br>")
        if len(消息内容)>2000:
            消息内容=消息内容[:1980]+"<br>(内容太长，已经截断)"
        for 组id in self.组解析(组):
            self.cc.execute("select f_text_email('rtta@rtfund.com',:z,:bt,:xxnr,:ts) from dual",z=组id,xxnr=消息内容,bt=标题,ts=消息保存天数)

    def 组解析(self,组):
        if 组:
            return [组]
        解析结果=[]
        for gid, in self.cc.execute("select group_id from sw3.sw_biz_contacts where swid='%s'" %(sw3.swid)):
            解析结果.append(gid)
        return 解析结果
