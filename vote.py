import urllib.request
import urllib.parse
import urllib.error
import json
import time
import requests
import re

proxy_handler = urllib.request.ProxyHandler({'http': '183.207.229.204:8000'})

opener = urllib.request.build_opener(proxy_handler)


request = urllib.request.Request('http://www.diaochapai.com/survey/adc99e84-22fd-4de0-ac30-6e77e6347952')
request.add_header('Host','www.diaochapai.com')
request.add_header('Connection','keep-alive')
request.add_header('Content-Length','131')
request.add_header('Pragma','no-cache')
request.add_header('Cache-Control','no-cache')
request.add_header('Content-Type','application/x-www-form-urlencoded; charset=UTF-8')
request.add_header('Accept-Encoding','gzip, deflate')
request.add_header("Referer","http://www.diaochapai.com/survey/adc99e84-22fd-4de0-ac30-6e77e6347952")
request.add_header('User-Agent','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.12 Safari/537.36')
request.add_header('Origin','http://www.diaochapai.com')
request.add_header('Accept','*/*')
request.add_header('Accept-Language','en-US,en;q=0.8')
request.add_header('X-Requested-With','XMLHttpRequest')
data = {"captcha":"24109","response":{"3271eabe-1200-4db3-b01c-8397c91fca20":{"choice":["c6cfa9a5-8832-421b-bcd8-1ef22e84b3dc"],"specify":{}}}}





p = re.compile("_vid=")
def Getvid(number):
    vid_list=[]
    for i in range(number):
        r = requests.get("http://www.diaochapai.com/survey/adc99e84-22fd-4de0-ac30-6e77e6347952")
        if r.status_code == 200:
            for cookie in r.cookies:
                match = p.search(str(cookie))
                if match:
                    vid_list.append(str(cookie)[13:50])
    return vid_list
vid_list = Getvid(100)
for i in range(100):
    request.add_header('Cookie','_vid=%s;captcha_token=bb238ba1-9e3d-42e8-8bc7-50db0cc9649a'%(vid_list[i]))
    try:
        response =opener.open(request,json.dumps(data).encode('utf-8'))
        html = response.read().decode('utf-8')
        print (vid_list[i],request.get_header("Cookie"))
    except urllib.error.HTTPError as e:
        print ("reason:",e.reason,"code:",e.code,"headers:",e.headers)
