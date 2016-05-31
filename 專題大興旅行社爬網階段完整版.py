# -*- coding: utf-8 -*-
import io

headers ={
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate, sdch',
'Accept-Language':'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4',
'Cache-Control':'max-age=0',
'Connection':'keep-alive',
'Cookie':'ASPSESSIONIDAATBRCDC=FFDIAEPAHOIIHKDNINIDKHPB; ASPSESSIONIDCCQBRDCD=KJPGBAMBKBBLCMDPHOKGBLEC; ASPSESSIONIDACRCQADD=CLAHNLICNIGAKHJKELJKKAGO; ASPSESSIONIDCCRARCDD=HFNOLHFDHHFPOLICKJJFGBPF; ASPSESSIONIDCARAQCCD=GPAAJPOAIIAOGPIIHOCKDILA; ASPSESSIONIDACRBRDDC=DLKGILLBMPLINLNOCGOBIEDB; __utmt=1; __utma=118944012.1033911542.1463499979.1464167947.1464181269.17; __utmc=118944012; __utmz=118944012.1463750313.10.4.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); _gat=1; __utmb=118944012.2.10.1464181269; _ga=GA1.3.1033911542.1463499979; ASPSESSIONIDAARCQDDC=IELBGHICFJMPKAEFDFGBBLEG',
'Host':'www.tahsintour.com.tw',
'Referer':'http://www.tahsintour.com.tw/html/sendai/PRO.html',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
}
projectList = []
tempDicC = []
urlform = 'http://www.tahsintour.com.tw/dir/tour/'         #下面url所共有的表頭網址,每個在urllist上的網址代表一個套裝行程(大興旅行社日本行)

urllist = [
    'SPK160307_ALL_JSS4D(2016_BR116165).asp','SPK20160411_BR116115_JSS5D(2016_6M8M).asp',\
           'SPK160321_BR116115_JSS5D(16_6M8M).asp','SPK160323_ALL_JSS7D(16_6M_after).asp',\
           'SPK151208_pak_JTT7D(16_0308_after).asp','SEN160202_ALL_JSD4D(160415_1110only).asp',\
           'SEN160202_ALL_JSD5D(160415_1110only).asp','TYO160412_ALL_JTT5D(2016).asp',\
           'TYO150511_ALL_JTT5D(2015_8M_after).asp','TYO150701_ALL_JTT5D(2015_8M_after).asp',\
           'TYO160217_ALL_JTT5D(16_BR196195only).asp','TYO140430_ALL_JTT5D(2014).asp',\
           'TYO150805_ALL_JTT5D(2015_9Mafter).asp','TYO151218_ALL_JTT5D(2016_after).asp',\
           'TYO151029_ALL_JTT5D(15_11M_after).asp','TYO160427_ALL_JTT5D(16_half).asp',\
           'HOK160429_CI154151_JKK5D(16_5M_after).asp','HOK151217_ALL_JKK5D(160424_after).asp',\
           'OSA151015_ALL_JOO5D(2015).asp','OSA160414_ALL_JOO5D(2016_summer_only).asp',\
           'OSA151223_JL816813_JOO5D(16_3M).asp','OSA160203_JOO5D(16_3M_after_four).asp',\
           'OSA160105_ALL_JOO5D(16_3M_after).asp','OSA160122_ALL_JOO5D(16_3M_after).asp',\
           'OSA140821_ALL_JOO5D(10M_after).asp','OSA150120_ALL_JOO5D(2015).asp',\
           'FOK160425_ALL_JFF5D(2016).asp','FOK160422_ALL_JFF5D(2016).asp',\
           'FOK160422_BR106105_JFF5D(16_5M_after).asp','FOK160510_BR_JFF5D(16_0501_1026).asp',\
           'FOK151021_BR_JFF5D(15_11M_after).asp','FOK160425_ALL_JFF5D(2016).asp',\
           'FOK150917_ALL_JFF5D(15_BR).asp','OKA160330_BR112113_JOO4D(16_4M_after).asp',\
           'OKA160330_ALL_JOO4D(16_4M_half).asp','OKA160406_ALL_JOO4D(2016).asp',\
           'OKA160406_ALL_JOO4D(2016_B).asp','TYO160427_ALL_JTT5D(16_half).asp',\
            'TYO160426_ALL_JTT5D(16_half).asp','TYO160425_ALL_JTT5D(16_FREE_S).asp',\
            'TYO160427_ALL_JTT5D(16_FREE_J).asp','TYO160425_ALL_JTT5D(16_FREE_G).asp',\
            'TYO160425_ALL_JTT5D(16_FREE_L).asp','TYO160427_ALL_JTT5D(16_FREE_B).asp',\
            'TYO160425_ALL_JTT5D(16_FREE_E).asp','TYO160425_ALL_JTT5D(16_FREE_K).asp',\
            'TYO160425_ALL_JTT5D(16_FREE_C).asp','TYO160425_ALL_JTT5D(16_FREE_N).asp',\
            'TYO160425_ALL_JTT5D(16_FREE_F).asp','TYO160425_ALL_JTT5D(16_FREE_D).asp',\
            'TYO160425_ALL_JTT5D(16_FREE_I).asp','TYO160425_ALL_JTT5D(16_FREE_M).asp',\
            'TYO160427_ALL_JTT5D(16_FREE_A).asp','SEN160429_ALL_JSD4D(160526only).asp',\
            'SPK160307_ALL_JSS4D(2016_BR116165).asp','SPK160307_ALL_JSS4D(2016_BR166115).asp',\
            'SEN160202_ALL_JSD4D(160415_1110only).asp','OKA160330_ALL_JOO4D(16_4M_half).asp',\
            'OKA160330_BR112113_JOO4D(16_4M_after).asp','OKA160406_ALL_JOO4D(2016_B).asp',\
            'OKA160406_ALL_JOO4D(2016).asp','princess-160309(1050104).asp'
]
#urllist所列的子網址:SPK:北海道; SEN:東北; TYO:東京; HOK:北陸立山; OKA:大阪/四國/沖繩; FOK:山陰.山楊/九州;OSA:大阪

tempDic = {'agency':'','prodNo':'','href':'','title':'','tour':''}  #創一個Dictionary
tempDic['agency'] = '大興旅行社'                                     #將旅社姓名塞入key是agency的tempDic
day = 'day{}'
#為了把每個套裝行程的每日行程(不固定天數)塞入tempDic中key是tour的value之中,須創造sub-Dictionary, day將以day.format(counrDay)的方式塞入
#projectList.append('agency':tempDic['agency'])                                                 #創造此projectList的目的是最後要將結果以appendix的方式加入此projectList
def geturl(url):
    import requests
    from bs4 import BeautifulSoup
    res =requests.get(url,headers = headers)
    if res.apparent_encoding == 'windows-1252':                    #有些網頁HTML之meta雖是big5,但用res.apparent_encoding抓出的卻是windows-1252
        res.encoding = 'big5'
    else:
        res.encoding = res.apparent_encoding                       #res.apparent_encoding是自動抓取各網頁encoding
    return BeautifulSoup(res.text,'html.parser')

with io.open('大興旅遊.txt', 'a',encoding='UTF-8') as f:       #將資料輸入檔案
    for url in urllist[0:]:
        urlform_url = urlform + url
        soup =geturl(urlform_url)
#        print urlform_url                                          #1.印出每日url
#        f.write(urlform_url)
        tempDic['prodNo'] = urlform_url.split('_')[0].split('/')[5]           #將行程ID塞入key是prodNo的tempDic
        tempDic['href'] = urlform_url                      #將網址塞入key是href的tempDic

        for ele in soup.select('.style154Copy1'):
#            print ele.text.strip()                                 #2.印出此套裝行程名稱
            f.write(ele.text.strip()+'/n')
            tempDic['title'] = ele.text.strip()               #將形成標題塞入key是title的tempDic

        countDay = 0
        tourDic = {}
        for ele in soup.select('.style57Copy003'):
            countDay = countDay + 1                                #每跑ㄧ次for迴圈,印出該個套裝行程ㄧ日的行程
#            print ele.text.strip()                                 #3.印出此套裝行程每日行程
            f.write(ele.text.strip()+'/n')
            tourDic[day.format(countDay)] = ele.text.strip()       #先造一個子Dict收集每日行程
#
        tempDic['tour'] = tourDic                                  #將每日行程收集起來塞到第一層的Disc
        ABC = tempDic.copy()                                       #這一步藉由copy的動做新建一個物件,以防止相同key值其value植被覆蓋
        projectList.append(ABC)

for ele in projectList:
    for key in sorted(ele):
        print key,ele[key]
print ('#############################################################')

import json
from json import load
with open('大興旅遊.json', 'w') as f:                               #轉成.json檔
    json.dump(projectList, f)