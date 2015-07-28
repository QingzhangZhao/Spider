# -*- coding: utf-8 -*-  
#---------------------------------------  
#   程序：华科电费系统爬虫 
#   版本：0.1
#   作者：zqz  
#   日期：2015-07-26  
#   语言：Python 3.4  
#   操作：输入所在的地理位置 
#   功能：用电查询。  
#---------------------------------------  




import urllib.request
import urllib.error
import string
import urllib.parse
import re
from bs4 import BeautifulSoup

#init global request
request = urllib.request.Request("http://202.114.18.218/main.aspx")
request.add_header('User-Agent','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.12 Safari/537.36')
request.add_header('HTTP_ACCEPT','text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' )
request.add_header('Referer:http','//202.114.18.218/main.aspx')
request.add_header('Content-Type','application/x-www-form-urlencoded')



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
#get  "__EVENTVALIDATION", "__VIEWSTATE" from textyq
def get_info_step2(programId,txtyq):
    info = get_info_step1(programId)
    data={
           " __EVENTTARGET":"txtyq",
           " __EVENTARGUMENT":"",
           " __LASTFOCUS":"",
           "programId":programId,
           "txtyq":txtyq,
           "Txtroom":"",
           "__VIEWSTATE":info[0],
           "__EVENTVALIDATION":info[1],
           "TextBox2":"",
           "TextBox3":"",
         }

    response = urllib.request.urlopen(request,urllib.parse.urlencode(data).encode('utf-8'))
    html=(response.read())
    soup = BeautifulSoup(html,'html.parser')
    viewstate = soup.find('input', {'id' : '__VIEWSTATE'})['value']
    ev = soup.find('input', {'id' : '__EVENTVALIDATION'})['value']
    return viewstate,ev

#get the result
def hust_query(programId,txtyq,txtld,Txtroom):
    info = get_info_step2(programId,txtyq)
    data={
    "__EVENTTARGET":"",
    "__EVENTARGUMENT":"",
    "__LASTFOCUS":"",
    "__VIEWSTATE":info[0],
    "__EVENTVALIDATION":info[1],
    "programId":programId,
    "txtyq":txtyq,
    "txtld":txtld,
    "Txtroom":Txtroom,
    "ImageButton1.x":'13',
    "ImageButton1.y":'14',
    "TextBox2":"",
    "TextBox3":""
    }
    response = urllib.request.urlopen(request,urllib.parse.urlencode(data).encode('utf-8'))
    html_data=(response.read()).decode("utf-8")
    pattern = re.compile(r'<input name="TextBox3".*?type="text".*?value="(.*)".*?readonly="readonly".*?id="TextBox3".*?/> ',re.S)
    match = pattern.search(html_data)
    
    pattern2 = re.compile(r'<input name="TextBox2" type="text" value="(.*)" readonly="readonly" id="TextBox2" />',re.S)
    match2 = pattern2.search(html_data) 
    
    pattern3 = re.compile(r'\s<td>(\d*\.\d*)</td><td>(\d*-\d*.*)</td>')
    store=[]
    for m in pattern3.finditer(html_data):
        store.append(m.group(1))
    aver = caculate(store)
    if match:
        print ("您的剩余电量:",match.group(1))
        print ("最后一次抄表时间:",match2.group(1))
        print ("您一天平均耗电:",aver)
        print ("按照当前速度，您一个月大约耗电:",aver*30)
        print ("预测你一个月需要交的电费为:",aver*3000/168)
        print ("预测你一个学期需要交的电费为:",aver*14000/168)
    else:
        print ("错误,请检查输入")

def caculate(store):
    sum=0
    count=0
    for i in range(1,7):
        if (float(store[i])-float(store[i-1]))>0:
            sum+=float(store[i])-float(store[i-1])
            count+=1
    aver = sum/count
    return aver





#get the info
p1 = str(input(u'请输入楼栋区域(如“东区”)：\n'))  
p2 = str(input(u'请输入楼号：(如”沁苑东十舍“)\n'))  
p3 = str(input(u'请输入楼层号(如”1层“)：\n'))  
p4 = int(input(u'请输入房间号(如”104“)：\n')) 

#start
hust_query(p1,p2,p3,p4)
