#!/usr/bin/python3
# -*- coding: utf8 -*-
#企微库。目前用于通过机器人发送企微消息。

import dbcfg,traceback

__all__=["qwmsg"]

class qwmsg(object):
    '企微消息库，把要发送的消息存入中间库待发'
    def __init__(self,chatroomname,appname=""):
        self.chatroomname=chatroomname
        self.appname=appname or '群机器人'
        cfg=dbcfg.use("swqiwei").cfg()
        self.db=dbcfg.use(cfg['d']['dbcfg'])   #配置数据库

    def msg(self,info):
        '发送文本消息'
        caller=traceback.extract_stack()[-2]
        callinfo=f"{caller.filename} {caller.lineno}行 调用者{caller.name}"
        print(callinfo)
        self.db.execute(f"insert into qwdl (id,REQUEST_TIME,qlmc,yymc,msgtype,ctext,app_name,IDENTITY_SIGN) values (qiwei_seq.nextval, sysdate, '{self.chatroomname}', '{self.appname}', 'text',:ctext,'事务平台','{callinfo}')", ctext=info)
        self.db.commit()
