# -*- coding: utf-8 -*-  
#Author: QingzhangZhao <zhaoqingzhanghust@gmail.com>


import argparse
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

parser = argparse.ArgumentParser(prog="hust_electricity_query",description="The %(prog)s program is used to query the electricity of hust",epilog="Just for fun")
parser.add_argument('--version', action='version', version='%(prog)s 1.0')
parser.add_argument('-i',nargs="?",dest="programId",choices=['东区','西区','韵苑二期','韵苑一期','紫菘'],required=True,help="选择区域")
parser.add_argument('-y',nargs="?",dest="txtyq",required=True,help="楼号，如沁苑东十舍")
parser.add_argument('-l',nargs="?",dest="txtld",required=True,help="楼层，如1层")
parser.add_argument('-r',nargs="?",dest="txtroom",type=int,required=True,help="房间号，如101")
args = parser.parse_args()


if __name__=='__main__':
    hust_query(args.programId,args.txtyq,args.txtld,args.txtroom)

