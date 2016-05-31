# -*- coding: utf-8 -*-
import io

projectList = []
tempDicC = []
headers ={
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate, sdch',
'Accept-Language':'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4',
'Cache-Control':'max-age=0',
'Connection':'keep-alive',
'Cookie':'_ga=GA1.3.92216041.1464523003',
'Host':'www.asuka.com.tw',
'Referer':'http://www.asuka.com.tw/AS_Japan.html',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
}
urlform = 'http://www.asuka.com.tw/tours/ASUKA/JP/'         #下面url所共有的表頭網址,每個在urllist上的網址代表一個套裝行程(大興旅行社日本行)
urllist = ['Hokkaido/TOMAMU_Summer/JP_HKD_TOMAMU_summer_5.html','Hokkaido/DOUTOU3PARKS_7/JP_HKD_DOUTOU_7.html',\
           'Hokkaido/Hokkaido_N_7/JP_HKD_N_7.html','Hokkaido/GARDEN_7/JP_HKD_GARDEN_7.html',\
           'Touhoku/SANRIKU_7/2015_JP_TH_SANRIKU_7_AKI.html','Touhoku/SHIRAKAMI_7/JP_TH_SHIRAKAMI_7_AKI.html',\
           'Touhoku/Nebuta_7/2015_JP_TH_Nebuta_7.html','Kantou/IZU_5/JP_KT_IZU_5_AKI.html',\
           'Kantou/IZU_5_2/PH_KT_IZU_5_2.html','Kantou/HAKONE_5/JP_KT_HAKONE_5_AKI.html',\
           'Chuubu/CHUUBU_7/JP_CB_CHUUBU_7.html','Chuubu/NOTO_6/JP_CB_NOTO_6.html',\
           'Chuubu/OOMACHI_SUM/JP_CB_OOMACHI_SUM.html','Kyoto/KYOTO1/JP_KY_KYOTO1_5.html',\
           'Kyoto/KYOTO2/JP_KY_KYOTO2_5.html','Kyoto/KYOTO3/JP_KY_KYOTO3_5.html',\
           'Kansai/SANIN_7/JP_KS_SANIN_7.html','Kansai/KUMANO/JP_KS_KUMANO_7.html',\
           'Sikoku/SIKOKU_7/JP_SK_SIKOKU_7.html','Sikoku/SIKOKU_5/JP_SK_SIKOKU_5.html',\
           'Kyuusyuu/YAKUSHIMA_5/JP_NKS_YAKUSHIMA_5.html','Kyuusyuu/KAGOSHIMA_7/JP_NKS_KAGOSHIMA_7.html'
           ]

headers2 ={
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate, sdch',
'Accept-Language':'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4',
'Cache-Control':'max-age=0',
'Connection':'keep-alive',
'Cookie':'_ga=GA1.3.92216041.1464523003',
'Host':'www.asuka.com.tw',
'Referer':'http://www.asuka.com.tw/AS_PH.html',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
}
urlform2 = 'http://www.asuka.com.tw/tours/PremierHolidays/JP/'
urllist2 = ['Hokkaido/SIRETOKO_7/PH_HKD_SIRETOKO_7.html','Chuubu/TACHIYAMA_5/PH_CB_TACHIYAMA_5.html',\
            'Chuubu/SADOGASHIMA&KUROBE_6/PH_CB_SADOGASHIMA&KUROBE_6.html','Chuubu/SADOGASHIMA_5/PH_CB_SADOGASHIMA_5.html',\
            'Kansai/NANKI_5/PH_KS_NANKI_5.html','Kansai/KYOTO_MIHO_5/PH_KS_KYOTO_MIHO_5.html',\
            'Kansai/SANIN_5/PH_KS_SANIN_5.html','Sikouku/SANYOU_5+1/PH_SK_SANYOU_5+1.html',\
            'Sikouku/NAOSHIMA_5+1/PH_SK_NAOSHIMA_5+1.html','Kyuusyuu/YAKUSHIMA_5/PH_NKS_YAKUSHIMA_5.html',\
            'Kyuusyuu/ATSUHIME_5/PH_NKS_ATSUHIME_5.html','Kyuusyuu/Mountaineering/PH_NKS_Mountaineering_5.html'
            ]
#urllist所列的子網址:SPK:北海道; SEN:東北; TYO:東京; HOK:北陸立山; OKA:大阪/四國/沖繩; FOK:山陰.山楊/九州;OSA:大阪

tempDic = {'agency':'','prodNo':'','href':'','title':'','tour':''}  #創一個Dictionary
tempDic['agency'] = '飛鳥旅行社'                                     #將旅社姓名塞入key是agency的tempDic
day = 'day{}'
#為了把每個套裝行程的每日行程(不固定天數)塞入tempDic中key是tour的value之中,須創造sub-Dictionary, day將以day.format(counrDay)的方式塞入
#projectList.append('agency':tempDic['agency'])                                                 #創造此projectList的目的是最後要將結果以appendix的方式加入此projectList
def geturl(url):
    import requests
    from bs4 import BeautifulSoup
    res =requests.get(url,headers = headers)
    res.encoding = 'utf-8'
    return BeautifulSoup(res.text,'html.parser')

def geturl2(url):
    import requests
    from bs4 import BeautifulSoup
    res =requests.get(url,headers = headers2)
    res.encoding = 'utf-8'
    return BeautifulSoup(res.text,'html.parser')

with io.open('專題飛鳥旅行社.txt', 'a',encoding='UTF-8') as f:       #將資料輸入檔案
    for url in urllist:
        urlform_url = urlform + url
        soup =geturl(urlform_url)
#        print urlform_url                                          #1.印出每日url
#        f.write(urlform_url)
        tempDic['prodNo'] = url.split('&')[0]           #將行程ID塞入key是prodNo的tempDic
        tempDic['href'] = urlform_url                      #將網址塞入key是href的tempDic
                      #將形成標題塞入key是title的tempDic
        titleDic={}
        for ele in soup.select('.tours_title'):
#            print ele.text.strip()                                 #2.印出此套裝行程名稱
            f.write(ele.text.strip()+'/n')
            titleDic['title'] = ele.text.strip()               #將主標題塞入key是title的titleDic

        for ele in soup.select('.tours_title_s'):
#            print ele.text.strip()                                 #2.印出此套裝行程名稱
            f.write(ele.text.strip()+'/n')
            titleDic['subtitle'] = ele.text.strip()               #將富標題塞入key是subtitle的titleDic

        tempDic['title'] = titleDic

        countDay = 0
        tourDic = {}
        for ele in soup.select('.tours_txt_daily td'):
            countDay = countDay + 1                                #每跑ㄧ次for迴圈,印出該個套裝行程ㄧ日的行程
#            print ele.text.strip()                                 #3.印出此套裝行程每日行程
#            f.write(ele.select('.eachdaily_title_day')[0].text.strip()+'/'+ele.select('.eachdaily_title_summary h2')[0].text.strip())
            tourDic[day.format(countDay)] = ele.text.strip()        #先造一個子Dict收集每日行程

        tempDic['tour'] = tourDic                                  #將每日行程收集起來塞到第一層的Disc
        ABC = tempDic.copy()                                       #這一步藉由copy的動做新建一個物件,以防止相同key值其value植被覆蓋
        projectList.append(ABC)
        print ('====================================================================')

    for url2 in urllist2:
        urlform_url = urlform2 + url2
        soup =geturl2(urlform_url)
    #        f.write(urlform_url)
        tempDic['prodNo'] = url2.split('/')[-1]          #將行程ID塞入key是prodNo的tempDic
        tempDic['href'] = url2                      #將網址塞入key是href的tempDic

        titleDic={}
        for ele in soup.select('.tours_title'):
#            print ele.text.strip()                                 #2.印出此套裝行程名稱
            f.write(ele.text.strip()+'/n')
            titleDic['title'] = ele.text.strip()               #將主標題塞入key是title的titleDic

        for ele in soup.select('.tours_title_s'):
#            print ele.text.strip()                                 #2.印出此套裝行程名稱
            f.write(ele.text.strip()+'/n')
            titleDic['subtitle'] = ele.text.strip()               #將富標題塞入key是subtitle的titleDic

        tempDic['title'] = titleDic

        countDay = 0
        tourDic = {}
        for ele in soup.select('.tours_txt_daily td'):
            countDay = countDay + 1                                #每跑ㄧ次for迴圈,印出該個套裝行程ㄧ日的行程
#            print ele.text.strip()                                 #3.印出此套裝行程每日行程
#            f.write(ele.select('.eachdaily_title_day')[0].text.strip()+'/'+ele.select('.eachdaily_title_summary h2')[0].text.strip())
            tourDic[day.format(countDay)] = ele.text.strip()        #先造一個子Dict收集每日行程

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
with open('飛鳥旅遊.json', 'w') as f:
    json.dump(projectList, f)