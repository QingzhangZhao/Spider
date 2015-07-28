# -*- coding: utf-8 -*-  
#---------------------------------------  
#   程序：华科电费系统爬虫 
#   版本：0.1
#   作者：zqz  
#   日期：2015-07-28  
#   语言：Python 3.4  
#   操作：运行，等待
#   功能：计算沁苑平均用电,发现哪些宿舍没人，发现土豪。  
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
       # print (txtyq,Txtroom,"您的剩余电量:",match.group(1))
        #print ("最后一次抄表时间:",match2.group(1))
        #print ("您一天平均耗电:",aver)
        if aver:
            if aver<0.3:
                print (txtyq,Txtroom,"宿舍无人")
        #print ("按照当前速度，您一个月大约耗电:",aver*30)
        #print ("预测你一个月需要交的电费为:",aver*3000/168)
        #print ("预测你一个学期需要交的电费为:",aver*14000/168)
    else:
        pass
        #print (txtyq,Txtroom,"无该仪表信息")

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
    print ("沁苑平均一天用电消耗:",aver)
    print ("最土豪寝室:",_Txtyq,_Txtroom,"平均一天用电:",_Cost)
    return aver


#get the info
#p1 = str(input(u'请输入楼栋区域(如“东区”)：\n'))  
#p2 = str(input(u'请输入楼号：(如”沁苑东十舍“)\n'))  
#p3 = str(input(u'请输入楼层号(如”1层“)：\n'))  
#p4 = int(input(u'请输入房间号(如”104“)：\n')) 

#start
for i in range(1,6):
    for j in range(1,7):
        for k in range(1,33):
            p3 = j
            p4 = p3*100+k
            if  i==1:
                p2="沁苑东九舍"
            elif i==2:
                p2="沁苑东十舍"
            elif i==3:
                p2="沁苑东十一舍"
            elif i==4:
                p2="沁苑东十二舍"
            elif i==5:
                p2="沁苑东十三舍"
            hust_query("东区",p2,p3,p4)
caculate_global(_Total,_Count)
