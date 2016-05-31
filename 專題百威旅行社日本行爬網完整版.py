# -*- coding: utf-8 -*-
import io

headers ={
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate, sdch',
'Accept-Language':'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4',
'Cache-Control':'max-age=0',
'Connection':'keep-alive',
'Cookie':'ASPSESSIONIDCCAQSDDQ=GBFGHDDBMNOHGPMJEFFCAIKC; _gat=1; __utmt=1; _ga=GA1.3.171846414.1464498219; __utma=82288005.171846414.1464498219.1464498219.1464498219.1; __utmb=82288005.4.10.1464498219; __utmc=82288005; __utmz=82288005.1464498219.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided)',
'Host':'www.bwt.com.tw',
'Referer':'http://www.bwt.com.tw/Travel/tour/Destination/Index.aspx?SN=1|Prom|sectPromSAREA00002',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
}
projectList = []
tempDicC = []
urlform = 'http://www.bwt.com.tw/eWeb/GO/L_GO_Type.asp?iMGRUP_CD='         #下面url所共有的表頭網址,每個在urllist上的網址代表一個套裝行程(大興旅行社日本行)

urllist = ['OKA21&DeptCity=TYU','OSA0516-R&DeptCity=TYU',\
           'OSA0516-7HF&DeptCity=TYU','FUK05CI01&DeptCity=TYU',\
           'TOH04-1&DeptCity=TYU',\
           'SPK0509-2&DeptCity=TYU','SPK0519&DeptCity=TYU',\
           'SPK0516&DeptCity=TYU','SPK0511&DeptCity=TYU',\
           'SPK0504&DeptCity=TYU','SPK0511A&DeptCity=TYU',\
           'SPK0511D&DeptCity=TYU','SPK0509-1&DeptCity=TYU',\
           'TYO0501B-10&DeptCity=TYU','TYO0507N&DeptCity=TYU',\
           'TYO0518-2&DeptCity=TYU','TYO0507-10&DeptCity=TYU',\
           'TYO0501-8&DeptCity=TYU','TYO0518-S&DeptCity=TYU',\
           'TYO0501B-4&DeptCity=TYU','TYO0301&DeptCity=TYU',\
           'TYO0501&DeptCity=TYU','TYO03&DeptCity=TYU',\
           'TYO05GRP&DeptCity=TYU','GITTYO02-1&DeptCity=TYU',\
           'GITTYO04-2&DeptCity=TYU','GITTYO05-4&DeptCity=TYU',\
           'GITTYO04-14&DeptCity=TYU',\
           'GITTYO05-15&DeptCity=TYU','TOY05-15&DeptCity=TYU',\
           'TOY0501A&DeptCity=TYU','NGO0604&DeptCity=TYU',\
           'NGO0601&DeptCity=TYU','NGO0508-2&DeptCity=TYU',\
           'ULA0501-2&DeptCity=TYU','GITNGO04-2&DeptCity=TYU',\
           'OSA0516-R&DeptCity=TYU','OSA0516-7HF&DeptCity=TYU',\
           'OSA0516-7&DeptCity=TYU','OSA0516-RCI&DeptCity=TYU',\
           'OSA0516-D&DeptCity=TYU','OSA0516-7H&DeptCity=TYU',\
           'OSA0516-7S&DeptCity=TYU','OSA0516-CH&DeptCity=TYU',\
           'OSA0515-12&DeptCity=TYU','OSA0515-9H&DeptCity=TYU',\
           'OSA0516-05&DeptCity=TYU','OSA0516-6S&DeptCity=TYU',\
           'OSA0515-9H&DeptCity=TYU','OSA0516-G&DeptCity=TYU',\
           'OSA0516-6HS&DeptCity=TYU','OSA0516-GP&DeptCity=TYU',\
           'OSA0516-GC&DeptCity=TYU','GITOSA02-1&DeptCity=TYU',\
           'GITOSA04-21&DeptCity=TYU','GITOSA05-M&DeptCity=TYU',\
           'GITOSA04-14&DeptCity=TYU','GITOSA04-15M&DeptCity=TYU',\
           'FUK05CI16&DeptCity=TYU','KOJ0501&DeptCity=TYU',\
           'KMI05CI02&DeptCity=TYU','FUK05CI11&DeptCity=TYU',\
           'FUK05CI17&DeptCity=TYU','FUK05CI01&DeptCity=TYU',\
           'KMI0503&DeptCity=TYU','KMI05CI03&DeptCity=TYU',\
           'KOJ05CI05&DeptCity=TYU','TAK0415-1&DeptCity=TYU',\
           'TAK0414-9&DeptCity=TYU','TAK0514-9&DeptCity=TYU',\
           'TAK0516-3&DeptCity=TYU','TAK0516-D&DeptCity=TYU',\
           'TAK0615-1&DeptCity=TYU','HIJ0515-TAK&DeptCity=TYU',\
           'HIJ0603&DeptCity=TYU','OKA14&DeptCity=TYU',\
           'OKA20&DeptCity=TYU','OKA21&DeptCity=TYU',\
           'OKA15&DeptCity=TYU','OKA05&DeptCity=TYU',\
#           'TYO0516-7&DeptCity=TYU','TYO0516&DeptCity=TYU','TOH0507&DeptCity=TYU'           #這三筆是箱根蘆之湖,鎌倉大佛,(日本第一美溪, 東北初夏5天)暫時找不到資料,先列出來
           ]
           #urllist共有86個(其中箱根蘆之湖,鎌倉大佛的頁面無法進入,故不列入urllist),TOH0507&DeptCity=TYU也查無相關資料(日本第一美溪, 東北初夏5天)

urllist2 = ['http://www.bwt.com.tw/Travel/tour/pg/self-guided.aspx?mgrup_cd=GITTYO04-13&DeptCity=TYU',\
            'http://www.bwt.com.tw/Travel/tour/pg/self-guided.aspx?mgrup_cd=GITOSA04-13&DeptCity=TYU',\
            'http://www.bwt.com.tw/Travel/tour/pg/self-guided.aspx?mgrup_cd=GITOSA04-13M&DeptCity=TYU',\
            'http://www.bwt.com.tw/Travel/tour/pg/self-guided.aspx?mgrup_cd=ISG02&DeptCity=TYU',\
            'http://www.bwt.com.tw/Travel/tour/pg/self-guided.aspx?mgrup_cd=ISG01&DeptCity=TYU']
#urllist所列的子網址:SPK:北海道; SEN:東北; TYO:東京; HOK:北陸立山; OKA:大阪/四國/沖繩; FOK:山陰.山楊/九州;OSA:大阪

tempDic = {'agency':'','prodNo':'','href':'','title':'','tour':''}  #創一個Dictionary
tempDic['agency'] = '百威旅行社'                                     #將旅社姓名塞入key是agency的tempDic
day = 'day{}'
#為了把每個套裝行程的每日行程(不固定天數)塞入tempDic中key是tour的value之中,須創造sub-Dictionary, day將以day.format(counrDay)的方式塞入
#projectList.append('agency':tempDic['agency'])                                                 #創造此projectList的目的是最後要將結果以appendix的方式加入此projectList
def geturl(url):
    import requests
    from bs4 import BeautifulSoup
    res =requests.get(url,headers = headers)
    res.encoding = 'utf-8'
    return BeautifulSoup(res.text,'html.parser')

with io.open('專題百威旅行社.txt', 'a',encoding='UTF-8') as f:       #將資料輸入檔案
    for url in urllist:
        urlform_url = urlform + url
        soup =geturl(urlform_url)
#        print urlform_url                                          #1.印出每日url
#        f.write(urlform_url)
        tempDic['prodNo'] = url.split('&')[0]           #將行程ID塞入key是prodNo的tempDic
        tempDic['href'] = urlform_url                      #將網址塞入key是href的tempDic
        print tempDic['href']
        for ele in soup.select('.h1bar'):
#            print ele.text.strip()                                 #2.印出此套裝行程名稱
            f.write(ele.select('h1')[0].text.strip()+'/n')
            tempDic['title'] = ele.select('h1')[0].text.strip()               #將形成標題塞入key是title的tempDic

        countDay = 0
        tourDic = {}
        for ele in soup.select('.eachdaily_title'):
            countDay = countDay + 1                                #每跑ㄧ次for迴圈,印出該個套裝行程ㄧ日的行程
#            print ele.text.strip()                                 #3.印出此套裝行程每日行程
            f.write(ele.select('.eachdaily_title_day')[0].text.strip()+'/'+ele.select('.eachdaily_title_summary h2')[0].text.strip())
            tourDic[day.format(countDay)] = ele.text.strip()        #先造一個子Dict收集每日行程

        tempDic['tour'] = tourDic                                  #將每日行程收集起來塞到第一層的Disc
        ABC = tempDic.copy()                                       #這一步藉由copy的動做新建一個物件,以防止相同key值其value植被覆蓋
        projectList.append(ABC)
        print ('====================================================================')

    for url2 in urllist2:
        soup =geturl(url2)
    #        f.write(urlform_url)
        tempDic['prodNo'] = url2.split('=')[-2].split('&')[0]           #將行程ID塞入key是prodNo的tempDic
        tempDic['href'] = url2                      #將網址塞入key是href的tempDic

        for ele in soup.select('.h1bar'):
    #            print ele.text.strip()                                 #2.印出此套裝行程名稱
            f.write(ele.select('h1')[0].text.strip()+'/n')
            tempDic['title'] = ele.select('h1')[0].text.strip()               #將形成標題塞入key是title的tempDic

        countDay = 0
        tourDic = {}
        for ele in soup.select('.flight_list td'):
            countDay = countDay + 1                                #每跑ㄧ次for迴圈,印出該個套裝行程ㄧ日的行程
    #            print ele.text.strip()                                 #3.印出此套裝行程每日行程
            f.write(ele.text.strip()+'/n')
            tourDic[day.format(countDay)] = ele.text.strip()            #先造一個子Dict收集每日行程

        tempDic['tour'] = tourDic                                  #將每日行程收集起來塞到第一層的Disc
        ABC = tempDic.copy()                                       #這一步藉由copy的動做新建一個物件,以防止相同key值其value植被覆蓋
        projectList.append(ABC)
        print ('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

for ele in projectList:
    for key in sorted(ele):
        print key,ele[key]
    print ('##########################################################')
import json
from json import load
with open('百威旅遊.json', 'w') as f:
    json.dump(projectList, f)