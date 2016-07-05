# -*- coding: utf-8 -*-
import io

projectList = []
miniprojectList = []      #是projectList的子集-只從title和tour抓景點名稱
wordList =[]

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
urllist = [#'Hokkaido/TOMAMU_Summer/JP_HKD_TOMAMU_summer_5.html','Hokkaido/DOUTOU3PARKS_7/JP_HKD_DOUTOU_7.html',\
           #'Hokkaido/Hokkaido_N_7/JP_HKD_N_7.html','Hokkaido/GARDEN_7/JP_HKD_GARDEN_7.html',\
           #'Touhoku/SANRIKU_7/2015_JP_TH_SANRIKU_7_AKI.html','Touhoku/SHIRAKAMI_7/JP_TH_SHIRAKAMI_7_AKI.html',\
           #'Touhoku/Nebuta_7/2015_JP_TH_Nebuta_7.html',\
           'Kantou/IZU_5/JP_KT_IZU_5_AKI.html',\
           'Kantou/IZU_5_2/PH_KT_IZU_5_2.html','Kantou/HAKONE_5/JP_KT_HAKONE_5_AKI.html',\
           #'Chuubu/CHUUBU_7/JP_CB_CHUUBU_7.html','Chuubu/NOTO_6/JP_CB_NOTO_6.html',\
           #'Chuubu/OOMACHI_SUM/JP_CB_OOMACHI_SUM.html',\
           'Kyoto/KYOTO1/JP_KY_KYOTO1_5.html',\
           'Kyoto/KYOTO2/JP_KY_KYOTO2_5.html','Kyoto/KYOTO3/JP_KY_KYOTO3_5.html',\
           'Kansai/SANIN_7/JP_KS_SANIN_7.html','Kansai/KUMANO/JP_KS_KUMANO_7.html'
           #'Sikoku/SIKOKU_7/JP_SK_SIKOKU_7.html','Sikoku/SIKOKU_5/JP_SK_SIKOKU_5.html',\
           #'Kyuusyuu/YAKUSHIMA_5/JP_NKS_YAKUSHIMA_5.html','Kyuusyuu/KAGOSHIMA_7/JP_NKS_KAGOSHIMA_7.html'
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
urllist2 = [#'Hokkaido/SIRETOKO_7/PH_HKD_SIRETOKO_7.html','Chuubu/TACHIYAMA_5/PH_CB_TACHIYAMA_5.html',\
            #'Chuubu/SADOGASHIMA&KUROBE_6/PH_CB_SADOGASHIMA&KUROBE_6.html','Chuubu/SADOGASHIMA_5/PH_CB_SADOGASHIMA_5.html',\
            'Kansai/NANKI_5/PH_KS_NANKI_5.html','Kansai/KYOTO_MIHO_5/PH_KS_KYOTO_MIHO_5.html',\
            'Kansai/SANIN_5/PH_KS_SANIN_5.html'
            #'Sikouku/SANYOU_5+1/PH_SK_SANYOU_5+1.html',\
            #'Sikouku/NAOSHIMA_5+1/PH_SK_NAOSHIMA_5+1.html','Kyuusyuu/YAKUSHIMA_5/PH_NKS_YAKUSHIMA_5.html',\
            #'Kyuusyuu/ATSUHIME_5/PH_NKS_ATSUHIME_5.html','Kyuusyuu/Mountaineering/PH_NKS_Mountaineering_5.html'
            ]
#urllist所列的子網址:Hokkaido:北海道; Touhoku:東北; Kantou:關東; Chuubu:中部; Kyoto:京都;
#Kansai:關西(包括:大阪、神戶、京都以至奈良); Sikoku:四國; Kyuusyuu:九州

tempDic = {'agency':'','prodNo':'','href':'','title':'','tour':''}  #創一個Dictionary
minitempDic = {'title':'','tour':''}
tempDic['agency'] = '飛鳥旅行社'                                     #將旅社姓名塞入key是agency的tempDic
day = 'day{}'
w = 'w{}'
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

countWord = 0
wordDic ={}
with io.open('專題飛鳥旅行社京京阪神.txt', 'a',encoding='UTF-8') as f:       #將資料輸入檔案
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
            countWord += 1
            print countWord
            print ele.text.strip()
            wordDic[w.format(countWord)] = ele.text.strip()


        for ele in soup.select('.tours_title_s'):
#            print ele.text.strip()                                 #2.印出此套裝行程名稱
            f.write(ele.text.strip()+'/n')
            titleDic['subtitle'] = ele.text.strip()               #將富標題塞入key是subtitle的titleDic
            countWord += 1
            print countWord
            print ele.text.strip()
            wordDic[w.format(countWord)] = ele.text.strip()

        tempDic['title'] = titleDic
        minitempDic['title'] = tempDic['title']                 #做成較小的子資料夾,只塞title和tour的景點名稱

        countDay = 0
        tourDic = {}

        for ele in soup.select('.tours_txt_daily td'):
            if 'DAY' not in ele.text.strip():
                countDay += 1                                #每跑ㄧ次for迴圈,印出該個套裝行程ㄧ日的行程
    #            print ele.text.strip()                                 #3.印出此套裝行程每日行程
    #            f.write(ele.select('.eachdaily_title_day')[0].text.strip()+'/'+ele.select('.eachdaily_title_summary h2')[0].text.strip())
                tourDic[day.format(countDay)] = ele.text.strip()        #先造一個子Dict收集每日行程
                for word in ele.text.split(u'—'):
                    for ws0 in word.split(u'/'):
                        for ws1 in ws0.split(u'／'):
                            for ws2 in ws1.split(u'】'):
#                                for ws3 in ws2.split(u'【'):
                                    for ws4 in ws2.split(u'　'):
                                        for ws5 in ws4.split('\n'):
                                            for ws6 in ws5.split('\t'):
                                                for ws7 in ws6.split(u'～'):
                                                    for ws8 in ws7.split(u'：'):
                                                        for ws9 in ws8.split(u'+++'):
                                                            for ws10 in ws9.split(u'（'):
                                                                for ws11 in ws10.split(u'）'):
                                                                    for ws12 in ws11.split(u'、'):
                                                                        for ws13 in ws12.split(u'─'):
                                                                            for ws14 in ws13.split(u'－'):
                                                                                for ws15 in ws14.split(u'・'):
                                                                                    for ws16 in ws15.split(u' '):
                                                                                        if ws16.strip() != "":
                                                                                            if ws16.strip() != u'◆':
                                                                                                print countWord
                                                                                                print ws16.strip()
                                                                                                print ('****************')
                                                                                                countWord += 1
                                                                                                wordDic[w.format(countWord)] = ws16.strip()


        tempDic['tour'] = tourDic                                  #將每日行程收集起來塞到第一層的Disc
        minitempDic['tour'] = tempDic['tour']                      #做成較小的子資料夾,只塞title和tour的景點名稱
        ABC = tempDic.copy()                                       #這一步藉由copy的動做新建一個物件,以防止相同key值其value植被覆蓋
        projectList.append(ABC)
        DEF = minitempDic.copy()                                   #做一個只抓景點名稱的子資料夾
        miniprojectList.append(DEF)

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
            countWord += 1
            print countWord
            print ele.text.strip()
            wordDic[w.format(countWord)] = ele.text.strip()

        for ele in soup.select('.tours_title_s'):
#            print ele.text.strip()                                 #2.印出此套裝行程名稱
            f.write(ele.text.strip()+'/n')
            titleDic['subtitle'] = ele.text.strip()               #將富標題塞入key是subtitle的titleDic
            countWord += 1
            print countWord
            print ele.text.strip()
            wordDic[w.format(countWord)] = ele.text.strip()

        tempDic['title'] = titleDic
        minitempDic['title'] = tempDic['title']                          #做成較小的子資料夾,只塞title和tour的景點名稱

        countDay = 0
        tourDic = {}
        for ele in soup.select('.tours_txt_daily td'):
            if 'DAY' not in ele.text.strip():
                countDay += 1                                #每跑ㄧ次for迴圈,印出該個套裝行程ㄧ日的行程
    #            print ele.text.strip()                                 #3.印出此套裝行程每日行程
    #            f.write(ele.select('.eachdaily_title_day')[0].text.strip()+'/'+ele.select('.eachdaily_title_summary h2')[0].text.strip())
                tourDic[day.format(countDay)] = ele.text.strip()        #先造一個子Dict收集每日行程
                for word in ele.text.split(u'—'):
                    for ws0 in word.split(u'/'):
                        for ws1 in ws0.split(u'／'):
                            for ws2 in ws1.split(u'】'):
 #                               for ws3 in ws2.split(u'【'):
                                    for ws4 in ws2.split(u'　'):
                                        for ws5 in ws4.split('\n'):
                                            for ws6 in ws5.split('\t'):
                                                for ws7 in ws6.split(u'～'):
                                                    for ws8 in ws7.split(u'：'):
                                                        for ws9 in ws8.split(u'+++'):
                                                            for ws10 in ws9.split(u'（'):
                                                                for ws11 in ws10.split(u'）'):
                                                                    for ws12 in ws11.split(u'、'):
                                                                        for ws13 in ws12.split(u'─'):
                                                                            for ws14 in ws13.split(u'－'):
                                                                                for ws15 in ws14.split(u'・'):
                                                                                    for ws16 in ws15.split(u' '):
                                                                                        if ws16.strip() != "":
                                                                                            if ws16.strip() != u'◆':
                                                                                                print countWord
                                                                                                print ws16.strip()
                                                                                                print ('****************')
                                                                                                countWord += 1
                                                                                                wordDic[w.format(countWord)] = ws16.strip()

        tempDic['tour'] = tourDic                                  #將每日行程收集起來塞到第一層的Disc
        minitempDic['tour'] = tempDic['tour']                      #做成較小的子資料夾,只塞title和tour的景點名稱
        ABC = tempDic.copy()                                       #這一步藉由copy的動做新建一個物件,以防止相同key值其value植被覆蓋
        projectList.append(ABC)
        DEF = minitempDic.copy()                                   #做一個只抓景點名稱的子資料夾
        miniprojectList.append(DEF)
    wordList.append(wordDic)                                   #造一個列出景點名稱的字典集
    print countWord
    print ('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

for ele in projectList:
    for key in sorted(ele):
        print key,ele[key]
    print ('##########################################################')
#做成json檔
import json
with open('飛鳥旅遊京京阪神.json', 'w') as f2:
    json.dump(projectList, f2)

#做成json檔
import json
with open('飛鳥旅遊京京阪神抓景點名稱.json', 'w') as f3:                               #轉成.json檔
    json.dump(miniprojectList, f3)                                         #只抓景點名稱

#做成json檔
import json
with open('飛鳥旅遊京京阪神抓景點名稱字典.json', 'w') as f4:                               #轉成.json檔
    json.dump(wordList, f4)                                         #抓景點名稱字典

f.close()
f2.close()
f3.close()
f4.close()

#下面數個步驟是將抓好的projectList灌入MongoDB,MongoDB的Server需開啟. 執行完會出現TypeError的錯誤,但沒關係,因為已經灌入資料庫了,最多寫try_except
try:
    from pymongo import MongoClient
    client = MongoClient()
    db = client['kuonanhong']
    collection = db[u'飛鳥旅遊京京阪神']
    #result = db.myCollection11.insert(projectList)     #這一行可以不用寫
    #db.myCollection13.insert(projectList)              #可以選擇此行直接寫collection之名稱
    collection.insert(projectList)                      #或先在上面定義collection的名稱, 都是要insert一個list
    #p.s.執行完會出現錯誤訊息:TypeError: ObjectId('577a7b4ca2985b0845991997') is not JSON serializable,但能可抓進mongodb

except TypeError:
    print('我們已經將飛鳥旅遊京京阪神景點名稱做成txt,json,也灌入MongoDB了!')