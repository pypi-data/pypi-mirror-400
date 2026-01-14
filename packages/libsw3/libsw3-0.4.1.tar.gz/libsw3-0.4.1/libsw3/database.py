#!/usr/bin/python3
# -*- coding: utf8 -*-

__all__=["c_oracle","c_database","c_mssql","c_tds","c_mysql"]

import time,base64,sys,json,urllib.request,ssl,os,datetime
import libsw3 as sw3

class c_database(object):
    def __init__(self,*连接参数1,**连接参数2):
        self.连接参数1=连接参数1
        self.连接参数2=连接参数2
        self.connected=False
    def commit(self):
        self.conn.commit()
    def 解析连接参数(self):
        self.sconn=""
        if len(self.连接参数1)>0:
            self.sconn=self.连接参数1[0]
            dh,_=os.path.splitdrive(os.getcwd())
            配置文件=os.path.join(dh,"/etc","dbconn.config.d","%s.cfg" %(self.sconn))
            if os.path.isfile(配置文件):
                配置数据=json.loads(open(配置文件).read())
                for i in 配置数据:
                    if i["db"]==self.name:
                        self.连接参数1=i["t"]
                        self.连接参数2=i["d"]
    def connect(self,*args,**kwargs):
        self.connected=True
        self.importdbdriver()
        if len(args)>0 or len(kwargs)>0:
            self.连接参数1=args
            self.连接参数2=kwargs
        self.解析连接参数()
        try:
            self.conn=self.dbdriver.connect(*self.连接参数1,**self.连接参数2)
        except:
            sw3.swexit(1,"数据库连接%s不成功" %(self.sconn))
        else:
            self.c=self.conn.cursor()
    def execute(self,ssql,*args,**kwargs):
        c=self.conn.cursor()
        c.execute(ssql,*args,**kwargs)
        return c
    def jg1(self,ssql,*args,**kwargs):
        '''根据sql返回1条结果'''
        c=self.conn.cursor()
        c.execute(ssql,*args,**kwargs)
        jg=c.fetchone()
        c.close()
        if jg==None:
            return
        if len(jg)==1:
            return jg[0]
        else:
            return jg
    def xg(self,ssql,*args,**kwargs):
        '''主要用于修改，执行完后附加commit操作'''
        c=self.execute(ssql,*args,**kwargs)
        self.commit()
        return c
    def __getattribute__(self,name):
        if name in ("c","conn") and not self.connected:
            self.connected=True
            self.connect()
        return object.__getattribute__(self,name)
    def __del__(self):
        if self.connected:
            self.conn.close()

class c_mysql(c_database):
    def importdbdriver(self):
        import pymysql
        self.dbdriver=pymysql
        self.name="mysql"

class c_tds(c_database):
    def importdbdriver(self):
        import pytds
        self.dbdriver=pytds
        self.name="tds"

class c_mssql():
    def __init__(self,sconn="",yslj=False,autocommit=False,raiseExp=True):
        global pymssql, configparser
        import pymssql, configparser
        self.sconn = sconn
        self.connected = False
        self.autocommit = autocommit
        self.raiseExp = raiseExp
        self.host,self.user,self.password,self.database = ('','','','')
        (not yslj) and self.connect()

    def convconn(self):
        if os.path.isfile("/etc/mssqlconn.cfg"):
            cfg = configparser.ConfigParser()
            cfg.read("/etc/mssqlconn.cfg")
            self.host = cfg.get(self.sconn,'host')
            self.user = cfg.get(self.sconn,'user')
            self.password = cfg.get(self.sconn,'password')
            self.database = cfg.get(self.sconn,'database')

    def connect(self, sconn=""):
        if sconn != "":
            self.sconn = sconn
            self.connected = False
        if self.connected:
            c = self.conn.cursor()
            try:
                c.execute("select 1")
            except Exception as e:
                self.connected = False
                print("SqlServer连接数据库异常：%s" % (e))
                if self.raiseExp:
                    raise  # 往上层抛
            else:
                return
        try:
            self.convconn()
            print(self.host,self.user,self.password,self.database)
            self.conn = pymssql.connect(host=self.host,user=self.user,password=self.password,database=self.database)
        except Exception as e:
            sw3.swexit(1, "SqlServer数据库连接%s不成功" % (self.sconn))
            error, = e.args
            if self.raiseExp:
                raise  # 往上层抛
        else:
            self.connected = True

    def execute(self,ssql,*args,**kwargs):
        (not self.connected) and self.connect()
        if not self.connected:
            return
        try:
            c=self.conn.cursor()
            c.execute(ssql,*args,**kwargs)
        except Exception as e:
            self.connected=False
            print("SqlServer执行异常：%s" % (e))
            if self.raiseExp:
                raise  # 往上层抛
            return
        return c

class c_oracle(c_database):
    def importdbdriver(self):
        import cx_Oracle
        self.dbdriver=cx_Oracle
        self.name="oracle"
    def droptable(self,tablename):
        if self.jg1("select count(1) from user_tables where table_name = upper('%s')" %(tablename))==1:
            self.c.execute("drop table %s purge" %(tablename))
    def execute2(self,ssql,**kwargs):
        try:
            list = []
            c = self.conn.cursor()
            c.execute(ssql, kwargs)
            col = c.description
            for item in c.fetchall():
                dict = {}
                for i in range(len(col)):
                    dict[col[i][0]] = item[i]
                list.append(dict)
        except self.dbdriver.DatabaseError as e:
            self.connected = False
            print("oracle执行异常：%s" % (e))
            if self.raiseExp:
                raise  # 往上层抛
            return
        return list
    def dp(self,open参数,目录名,文件名,parameter=[],remap=[],ft=[]):    #类似impdp导入数据
        '''
使用DBMS_DATAPUMP包操作impdp和expdp的文档可参考 https://docs.oracle.com/database/121/ARPLS/d_datpmp.htm#ARPLS631
调用示例如 xxx.dp(['IMPORT','FULL'],"oracle数据目录","导入文件名（会自动加上.dmp)", parameter=[["TABLE_EXISTS_ACTION","REPLACE"]], remap=[["REMAP_SCHEMA","导出用户","导入用户"]], ft=[[]])

open参数实际上是提交到DBMS_DATAPUMP.open的参数，详情请参考oracle参数（下同），常用的是：
参数1选择 EXPORT 或者 IMPORT 表示导出或者导入
参数2可选择 FULL SCHEMA TABLE TABLESPACE

parameter参数用于处理dbms_datapump.set_parameter，常用的是：
TABLE_EXISTS_ACTION     用于处理表已经存在时，可选择的参数是：TRUNCATE, REPLACE, APPEND, 和 SKIP.

remap参数用于处理dbms_datapump.METADATA_REMAP，常用的是：
REMAP_SCHEMA    用于导出和导入非同一用户时
REMAP_TABLESPACE    用于导出和导入非同一表空间时

ft参数用于处理DBMS_DATAPUMP.METADATA_FILTER，常用的是：

'''
        (not self.connected) and self.connect()
        目录名=目录名.upper()
        c=self.conn.cursor()
        dp号=c.var(self.dbdriver.NUMBER)
        c.callfunc('DBMS_DATAPUMP.open',dp号,open参数)
        dp=int(dp号.getvalue())
        c.execute("BEGIN DBMS_DATAPUMP.add_file(handle=> %d,filename=>'%s.dmp',directory=>'%s',filetype=>DBMS_DATAPUMP.KU$_FILE_TYPE_DUMP_FILE); END;" %(dp,文件名,目录名))
        c.execute("BEGIN DBMS_DATAPUMP.add_file(handle=> %d,filename=>'%s_%s.log',directory=>'%s',filetype=>DBMS_DATAPUMP.KU$_FILE_TYPE_LOG_FILE); END;" %(dp,文件名,open参数[0].lower(),目录名))
        for 项目,内容 in ft:
            c.callproc("dbms_datapump.METADATA_FILTER",[dp,项目,内容])
        for 项目,内容 in parameter:
            c.callproc("dbms_datapump.set_parameter",[dp,项目,内容])
        for 项目,旧值,新值 in remap:
            c.callproc("dbms_datapump.METADATA_REMAP",[dp,项目,旧值,新值])
        try:
            c.callproc("DBMS_DATAPUMP.start_job",[dp])
        except self.dbdriver.DatabaseError as e:
            sql_getstatus='''
DECLARE
    job_state VARCHAR2(2000);
    status  ku$_Status;
BEGIN
    DBMS_DATAPUMP.GET_STATUS(%d,DBMS_DATAPUMP.KU$_STATUS_JOB_STATUS,0,job_state,status);
    DBMS_OUTPUT.put_line(job_state);
END;''' %(dp)
            print(sql_getstatus)
            c.callproc("dbms_output.enable")
            c.execute(sql_getstatus)
            self.dbms_output(c)
        job_state=c.var(self.dbdriver.STRING)
        c.callproc("DBMS_DATAPUMP.WAIT_FOR_JOB",[dp,job_state])
    def dbms_output(self,cursor,n=100):
        '''打印dbms_output数据，注意要预先 callproc("dbms_output.enable") '''
        lines = cursor.arrayvar(self.dbdriver.STRING, n)
        numlines = cursor.var(self.dbdriver.NUMBER)
        numlines.setvalue(0,n)  # fetch 'n' lines at a time
        while True:
            cursor.callproc("dbms_output.get_lines",(lines, numlines))
            num_of_lines = int(numlines.getvalue())
            if num_of_lines != 0:
                for line in lines.getvalue()[:num_of_lines]:
                    print(line)
            else:
                break        
    def inslist(self,tablename,data,collist=""):
        '''在表中直接插入数据'''
        (not self.connected) and self.connect()
        if collist=="":
            ssql="insert into %s values(" %(tablename)
        else:
            ssql="insert into %s (%s) values(" %(tablename,collist)
        for i in range(len(data)):
            ssql="%s:%d," %(ssql,i)
        ssql="%s)" %(ssql[:-1])
        c=self.conn.cursor()
        c.execute(ssql,data)
    def tablecreatesql(self,tablename): #获取表的生成脚本
        c=self.conn.cursor()
        sql='''
BEGIN
    DBMS_METADATA.SET_TRANSFORM_PARAM(-1,'TABLESPACE',false);
    DBMS_METADATA.SET_TRANSFORM_PARAM(-1,'STORAGE',false);
    DBMS_METADATA.SET_TRANSFORM_PARAM(-1,'SEGMENT_ATTRIBUTES',false);
    DBMS_METADATA.SET_TRANSFORM_PARAM(-1,'PRETTY',false);
END;
'''
        c.execute(sql)
        ssql=self.jg1("SELECT dbms_metadata.get_ddl('TABLE','%s') FROM DUAL" %(tablename.upper())).read()
        ssql='create table "%s" %s' %(tablename.upper(),ssql[ssql.find("("):])
        return ssql
