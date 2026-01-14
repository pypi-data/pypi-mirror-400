#!/usr/bin/python3
# -*- coding: utf8 -*-

__all__=["可靠邮件","普通邮件","create_html_table","表格邮件"]

from email import encoders
import smtplib,configparser,os
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
import libsw3 as sw3
sw3.__all__=sw3.__all__ + __all__

class 普通邮件(object):   #直接发送，如果发送失败，可能导致程序崩溃或者邮件发送失败
    def __init__(self,发送者,标题,正文,接收,抄送=[],暗送=[],邮件类型="plain",重要性=1):
        self.参数=[发送者,标题,正文,接收,抄送,暗送]
        self.msg=MIMEMultipart()
        self.msg.attach(MIMEText(正文, 邮件类型, 'gbk'))
        self.msg['Subject'] = 标题
        self.msg['From'] = "%s@rtfund.com" %(发送者)
        self.dz=[]
        self.msg['To'] = ','.join(self.解析地址(接收))
        self.msg['Cc'] = ','.join(self.解析地址(抄送))
        self.msg['Bcc'] = ','.join(self.解析地址(暗送))
        if 重要性 > 1:
            self.msg['Importance'] = 'High'
        if 重要性 < 1:
            self.msg['Importance'] = 'Low'
    def 解析地址(self,地址):
        if type(地址)!=type([]):
            地址=[地址]
        self.dz=self.dz + 地址
        return 地址
    def attachfile(self,attname,文件名):
        self.attach(attname,open(文件名, 'rb').read())
    def attach(self,attname,att):
        attmt = MIMEBase('application', 'octet-stream')
        attmt.set_payload(att)
        attmt.add_header('Content-Disposition', 'attachment', filename=('gbk', '', attname) )
        encoders.encode_base64(attmt)
        self.msg.attach(attmt)
    def send(self):
        swmailcfg = configparser.ConfigParser()
        dh,_=os.path.splitdrive(os.getcwd())
        swmailcfg.read(os.path.join(dh,"/etc","swmail.cfg"))
        cfg=swmailcfg[self.参数[0]]
        smtp=smtplib.SMTP(cfg["smtpserver"])
        smtp.starttls()
        smtp.login(cfg["user"],cfg["password"])
        if self.dz!=['']:
            smtp.sendmail(cfg["from"],self.dz,self.msg.as_string())
        smtp.close()

class 可靠邮件(object):   #把数据保存在本地硬盘，使用另一个扫描程序进行发送
    def __init__(self,发送者,标题,正文,接收,抄送=[],暗送=[]):
        self.参数=[发送者,标题,正文,接收,抄送,暗送]
    
def create_html_table(headlist,keylist,datalist):   #生成table样式的html内容。参数：表头文本，字段显示顺序，要显示的数据（每一行是一个字典）
    _html, _head, _trs = ("", "<tr>", "")
    if len(headlist)==len(keylist):
        # head
        for headtitle in headlist:
            _head = _head + "<th>" + headtitle + "</th>"
        _head = _head + "</tr>"
        # body
        for d in datalist:
            _tr = "<tr>"
            for key in keylist:
                _tr = _tr + "<td>" + d.get(key,"") + "</td>"
            _tr = _tr + "</tr>"
            _trs = _trs + _tr
        _html = HTML_TEMP_TABLE.replace("$THEAD_TR$", _head).replace("$TBODY_TR$", _trs)
    return _html

class 表格邮件(object): #新的邮件处理，不同接收人可以有不同的内容，自动展开表格
    邮件头='''
<html>
	<head>
		<style>
		table {
			border-collapse: collapse;
		}
		th,td {
			 padding: 8px;
		}
		th {
			border: 1px solid #777;
			text-align: left;
			font-size:14px;
		}
		td {
			border: 1px solid #777;
			font-size:13px;
		}
		</style>
	</head>
	<body>
'''
    表头='''
<table width=90%%>
<thead>
%s
</thead>
<tbody>
'''
    def __init__(self):
        self.接收人=set()
        self.正文内容={}
    def 增加内容(self,接收人列表,内容):
        '接收人列表可以是字符串表示单个接收人，也可以是列表表示多个接收人，接收人每人增加相应内容,'
        if type(接收人列表)==type(""):
            接收人列表=[接收人列表]
        for 接收人 in 接收人列表:
            if 接收人 not in self.接收人:
                self.接收人.add(接收人)
                self.正文内容[接收人]=self.邮件头
            self.正文内容[接收人]=self.正文内容[接收人]+内容
    def 建立表格(self,表头行,行模板=""):
        '''清空当前接收人，构建表头行
        表头行可以是字符串如<tr><th>??</th></tr>这样，也可以是列表或者空格隔开的表头行数据
        行模板用来在输出行是字典时格式化用，如<tr><td>{字段名1}</td>...</tr>，可以用列表或者空格隔开的字段名清单，或者直接是字符串
        '''
        self.当前接收人=set()
        self.表格内容={}
        self.表头行=表头行
        self.行模板=行模板
        if type(表头行)==type('') and 表头行.find("<tr>")>0:return
        if type(表头行)==type(''):
            表头行=表头行.split()
        self.表头行="<tr><th>"+"</th><th>".join(表头行)+"</th></tr>"
        self.行模板=行模板 or "<tr><td>{"+"}</td><td>{".join(表头行)+"}</td></tr>"
    def 增加表格行(self,接收人列表,行):
        '同一个表格，不同的接收人会有不同的内容，所以增加表格行的时候要设置接收人，接收人列表可以是字符串表示单个接收人，也可以是列表'
        if type(接收人列表)==type(""):
            接收人列表=[接收人列表]
        for 接收人 in 接收人列表:
            if 接收人 not in self.表格内容:
                self.表格内容[接收人]=[]
            self.表格内容[接收人].append(行)
    def 结束表格(self,表宽度="90%"):
        '展开表格内容，更新每个人的表格'
        for 接收人 in self.表格内容:
            表内容=self.表头 %(self.表头行)
            for 内容 in self.表格内容[接收人]:
                if type(内容)==type(''):
                    表内容=表内容+"\n"+内容
                else:
                    表内容=表内容+"\n"+self.行模板.format(**内容)
            表内容=表内容+"\n"+"</tbody>\n</table>\n"
            self.增加内容(接收人,表内容)
    def 发送(self,标题,发件邮箱="rtta"):
        for 接收人 in self.接收人:
            if sw3.istest:
                yj=sw3.普通邮件(发件邮箱,标题,self.正文内容[接收人]+f'\n发送给{接收人}</body>\n</html>\n',sw3.testmail,邮件类型="html")
            else:
                yj=sw3.普通邮件(发件邮箱,标题,self.正文内容[接收人]+'\n</body>\n</html>\n',接收人,邮件类型="html")
            yj.send()

HTML_TEMP_TABLE = '''
<html>
	<head>
		<style>
		table {
			border-collapse: collapse;
		}
		th,td {
			 padding: 8px;
		}
		th {
			background:#555;
			border: 1px solid #777;
			text-align: left;
			color: #fff;
			font-size:14px;
		}
		td {
			border: 1px solid #777;
			font-size:13px;
		}
		</style>
	</head>
	<body>
		<table align="center">
			<thead>
				$THEAD_TR$
			</thead>
			<tbody>
				$TBODY_TR$
			</tbody>
		</table>
	</body>

</html>
'''

