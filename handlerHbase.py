#!/usr/bin/env python
# -*- coding:utf-8 -*-
import requests
import json
import sys
import time
import datetime
import traceback


#**************************#
#和thrift相关，操作hbase
#**************************#
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from hbase import Hbase
from hbase.ttypes import *
transport = TSocket.TSocket('localhost', 9090)
transport = TTransport.TBufferedTransport(transport)
protocol = TBinaryProtocol.TBinaryProtocol(transport)
client = Hbase.Client(protocol)
transport.open()

#*****************#
#和solr相关
#*****************#
JSON_HEADER = {'content-type': 'application/json',}
URL = "http://IP:8983/solr/sixduoa/update/json/docs"
SELECTURL = "http://IP:8983/solr/sixduoa/select?"

chatfilter = {'q':'*:*','wt':'json','indent':True,'rows':'20', 'fl':'msg_id','fq':'fromto:'+'','fq':'fromto:'+'','sort':'id '+ 'desc','cursorMark':'*' }       #单聊天消息查询
groupchatfilter = {'q':'*:*','wt':'json','indent':True,'rows':'20', 'fl':'id,msg_id','fq':'fromto:'+'','sort':'id '+'desc','cursorMark':'*' }                        #群聊天消息查询
#filter = '''q=*%3A*&wt=json&indent=true&start=19&rows=21'''
#filter = '''q=*%3A*&wt=json&indent=true&id=123&sort=id+desc&cursorMark=*'''
#data = {'q':'*:*','wt':'json','indent':True,'start':'19' ,'rows':'21','date':['2015-04-01' 'TO' '2015-12-21'], 'fl':'date','sort':'date'+'+'+'desc' }

TABLENAME = 'tableName'  #表名
COLUMN = 'tableName'     #列簇

class ChatHandler:
      def __init__ (self):
            pass
      #读取hbase数据
      def getHbaseDta(self,rowkey):
            try:
                  chatList = {}
                  p = client.getRow(TABLENAME, rowkey, attributes=None)
                  if p:
                        for k,v in p[0].columns.items():
                              chatList[k[k.index(':')+1:]] = json.loads(v.value)
                        return chatList
            except:
                  print traceback.format_exc()
                  pass
            return chatList
      #插入hbase数据
      def putHbaseData(self,data):
            try:
                  if not data:
                        return  None
                  mu = []
                  #dataList = {"messageId":'',"conversationChatter":'','mfrom':'','mto':'','isGroup':'','groupSenderName':'','requerBeforeSend':'','requireOnServer':'','deliveryState':'','messageBodies':'','ext':'','mtimesstamp':'','isRead':'','isReadAcked':'','isDeliveredAcked':'','isAnonymous':''}
                  for key,value in data.iteritems():
                        #print key,value
                        mu.append ( Mutation(isDelete=0,column = COLUMN + ':' + key,value = json.dumps(value) ))    #value 为text
                  timestamp = int( time.time()*1000 )         #存储记录的时间
                  try:
                        p = client.mutateRowTs( TABLENAME, data.get( 'msg_id','error'), mutations = mu, timestamp = timestamp, attributes = None)
                        payload = {'msg_id': data.get( 'msg_id','error') ,"fromto":[data.get( "from",''),data.get( 'to','')] ,"chat_type":data.get( 'chat_type',''),"id":data.get('timestamp',0)}
                        self.addIndexData (URL, payload)
                  except:
                        print traceback.format_exc()
                        pass
                  return True
            except:
                  traceback.format_exc()
                  pass
            return  False
      # 添加索引数据
      def addIndexData (self,url, payload={}):      #payload = {"BUSS":1,"user":'test','woman':'test'}
            try:
                  auth = ''
                  reponse = requests.post(url, data = json.dumps(payload), headers = JSON_HEADER, auth = auth)
                  if reponse.status_code == requests.codes.ok:
                        return reponse.text
                  else:
                        return reponse.text
            except:
                  print traceback.format_exc()
                  pass
      # 读取索引数据
      def readRquestIndexData (self,filter):       # filter = '''q=*%3A*&wt=json&indent=true&id=123&sort=id+desc&cursorMark=*'''
            try:
                  auth = ''
                  data = {'q':'*:*','wt':'json','indent':True,'rows':'20', 'fl':'msg_id','sort':'id '+'desc','cursorMark':'*' }
                  reponse = requests.get( URL, params = data,headers = JSON_HEADER, auth = auth)
                  if reponse.status_code == requests.codes.ok:
                        data = json.loads(reponse.text)
                        data["response"]["docs"]
                        return reponse.text
                  else:
                        return reponse.text
            except:
                  print traceback.format_exc()
                  pass
       #获取数据库中的信息
      def getGroupChatMessages(self,groupID,cursorMark = None):
            try:
                  auth = ''
                  groupchatfilter['fq'] = 'fromto:'+ groupID
                  if cursorMark:
                        groupchatfilter['cursorMark'] = cursorMark
                  reponse = requests.get( SELECTURL, params = groupchatfilter,headers = JSON_HEADER, auth = auth)
                  if reponse.status_code == requests.codes.ok:
                        data = json.loads(reponse.text)
                        chatList = map(self.getHbaseDta,map(lambda x : x['msg_id'][0], data["response"]["docs"] ))
                        if chatList:
                              chatList.append( {'nextPage':data["nextCursorMark"]} )
                              return chatList
                  else:
                        return reponse.text
                  pass
            except:
                  print traceback.format_exc()
                  pass
            return []                  
            
