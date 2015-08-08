# -*- coding: utf-8 -*-  
#Author: QingzhangZhao <zhaoqingzhanghust@gmail.com>

import urllib.request
import urllib.error
import string
import urllib.parse
import re
import os
from bs4 import BeautifulSoup
import threading
import queue
import time

q = queue.Queue(0)
#init global request
request = urllib.request.Request("http://202.114.18.218/main.aspx")
request.add_header('User-Agent','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.12 Safari/537.36')
request.add_header('HTTP_ACCEPT','text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' )
request.add_header('Referer:http','//202.114.18.218/main.aspx')
request.add_header('Content-Type','application/x-www-form-urlencoded')

pattern = re.compile(r'<input name="TextBox3".*?type="text".*?value="(.*)".*?readonly="readonly".*?id="TextBox3".*?/> ',re.S)
pattern2 = re.compile(r'<input name="TextBox2" type="text" value="(.*)" readonly="readonly" id="TextBox2" />',re.S)
pattern3 = re.compile(r'\s<td>(\d*\.\d*)</td><td>(\d*-\d*.*)</td>')

info2_9=[]
info2_10=[]
info2_11=[]
info2_12=[]
info2_13=[]

_Total=0.0
_Count=0
_Txtyq="沁苑东九舍"
_Txtroom="101"
_Cost=0


#get  "__EVENTVALIDATION", "__VIEWSTATE" from programId
def get_info_step1(programId):
    response = urllib.request.urlopen(request)
    html=(response.read())
    soup = BeautifulSoup(html,'html.parser')
    
    viewstate = soup.find('input', {'id' : '__VIEWSTATE'})['value']
    ev = soup.find('input', {'id' : '__EVENTVALIDATION'})['value']

    data={
           " __EVENTTARGET":"programId",
           " __EVENTARGUMENT":"",
           " __LASTFOCUS":"",  
           "programId":programId,
           "Txtroom":"",
           "__EVENTVALIDATION":ev,
           "__VIEWSTATE":viewstate,
           "TextBox2":"",
           "TextBox3":"",
         }
    response = urllib.request.urlopen(request,urllib.parse.urlencode(data).encode('utf-8'))
    html=(response.read())
    soup = BeautifulSoup(html,'html.parser')
    viewstate = soup.find('input', {'id' : '__VIEWSTATE'})['value']
    ev = soup.find('input', {'id' : '__EVENTVALIDATION'})['value']
    return viewstate,ev

info1 = get_info_step1("东区")
#get  "__EVENTVALIDATION", "__VIEWSTATE" from textyq
def get_info_step2(programId,txtyq):
    data={
           " __EVENTTARGET":"txtyq",
           " __EVENTARGUMENT":"",
           " __LASTFOCUS":"",
           "programId":programId,
           "txtyq":txtyq,
           "Txtroom":"",
           "__VIEWSTATE":info1[0],
           "__EVENTVALIDATION":info1[1],
           "TextBox2":"",
           "TextBox3":"",
         }

    response = urllib.request.urlopen(request,urllib.parse.urlencode(data).encode('utf-8'))
    html=(response.read())
    soup = BeautifulSoup(html,'html.parser')
    viewstate = soup.find('input', {'id' : '__VIEWSTATE'})['value']
    ev = soup.find('input', {'id' : '__EVENTVALIDATION'})['value']
    return viewstate,ev

for i in range(1,6):
    if  i==1:
        info2_9=get_info_step2("东区","沁苑东九舍")
    elif i==2:
        info2_10=get_info_step2("东区","沁苑东十舍")
    elif i==3:
        info2_11=get_info_step2("东区","沁苑东十一舍")
    elif i==4:
        info2_12=get_info_step2("东区","沁苑东十二舍")
    elif i==5:
        info2_13=get_info_step2("东区","沁苑东十三舍")

#get the result
def hust_query(programId,txtyq,txtld,Txtroom):
    if  txtyq=="沁苑东九舍":
        info=info2_9
    elif txtyq=="沁苑东十舍":
        info=info2_10
    elif txtyq=="沁苑东十一舍":
        info=info2_11
    elif txtyq=="沁苑东十二舍":
        info=info2_12
    elif txtyq=="沁苑东十三舍":
        info=info2_13


    data={
    "__EVENTTARGET":"",
    "__EVENTARGUMENT":"",
    "__LASTFOCUS":"",
    "__VIEWSTATE":info[0],
    "__EVENTVALIDATION":info[1],
    "programId":programId,
    "txtyq":txtyq,
    "txtld":str(txtld)+"层",
    "Txtroom":Txtroom,
    "ImageButton1.x":'13',
    "ImageButton1.y":'14',
    "TextBox2":"",
    "TextBox3":""
    }
    response = urllib.request.urlopen(request,urllib.parse.urlencode(data).encode('utf-8'))
    html_data=(response.read()).decode("utf-8")
    match = pattern.search(html_data)
    #match2 = pattern2.search(html_data) 
    store=[]
    for m in pattern3.finditer(html_data):
        store.append(m.group(1))
    global _Total 
    global _Count 
    global _Cost
    global _Txtyq
    global _Txtroom
    if store:
        aver = caculate(store)
        if aver>0.3:
            _Total += aver
            _Count += 1
            if aver > _Cost:
                _Cost=aver
                _Txtyq=txtyq
                _Txtroom=Txtroom

    if match:
        if aver:
            if aver<0.3:
                print (txtyq,Txtroom,"宿舍无人")
    else:
        pass

#caculate the power cosumtion
def caculate(store):
    sum=0
    count=0
    for i in range(1,7):
        if(float(store[i])-float(store[i-1]))>=0:
            sum+=float(store[i])-float(store[i-1])
            count+=1
    aver = sum/count
    return aver

def caculate_global(total,count):
    aver = total/count
    global _Cost
    global _Txtyq
    global _Txtroom
    print ("该楼平均一天用电消耗:",aver)
    print ("最土豪寝室:",_Txtyq,_Txtroom,"平均一天用电:",_Cost)
    return aver

class Info():
    def __init__(self,programId,txtyq,txtld,txtroom):
        self._programId=programId
        self._txtyq=txtyq
        self._txtld=txtld
        self._txtroom=txtroom

def gen_queue(str):
    for j in range(1,7):
        for k in range(1,33):
            p3 = j
            p4 = p3*100+k
            p2=str
            q.put(Info("东区",p2,p3,p4))
def run(str):
    for j in range(1,7):
            for k in range(1,33):
                p3 = j
                p4 = p3*100+k
                p2=str
                hust_query("东区",p2,p3,p4)
    caculate_global(_Total,_Count)

class Mythread(threading.Thread):
    """Just for testing"""
    def __init__(self,jobq):
        threading.Thread.__init__(self,)
        self._jobq=jobq
    def run(self):
        while True:
            if self._jobq.qsize()>0:
                info=self._jobq.get()
                #print ("start at %s" %(time.ctime()))
                hust_query(info._programId,info._txtyq,info._txtld,info._txtroom)
            else:
                break

def get_queue():
    gen_queue("沁苑东九舍")
    gen_queue("沁苑东十舍")
    gen_queue("沁苑东十一舍")
    gen_queue("沁苑东十二舍")
    gen_queue("沁苑东十三舍")

if __name__=='__main__':
    get_queue()
    for x in range(100):
        Mythread(q).start()
