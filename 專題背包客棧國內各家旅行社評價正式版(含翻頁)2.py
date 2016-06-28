# -*- coding: utf-8 -*-
import re
import requests
import io

headers ={
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate, sdch',
'Accept-Language':'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4',
'Cache-Control':'max-age=0',
'Connection':'keep-alive',
'Cookie':'__gads=ID=15f3ac54b8ee1d34:T=1464841777:S=ALNI_MbFeQ63nF_ji_DobOd9QOnq6NjXqA; bbkz_infobar=30; bbkz_sessionhash=8a2f0e348c777b03d93ab3669c86db1f; bbkz_lastvisit=1464841777; bbkz_lastactivity=0; _ga=GA1.3.628503079.1464841778; _gat=1',
'Host':'www.backpackers.com.tw',
'Referer':'https://www.google.com.tw/',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
}
projectList = []
urlform = 'http://www.backpackers.com.tw/forum'
urllist = [
           '/forumdisplay.php?f=108&order=desc'
           ]

def geturl(url):                                          #這函式是要自動化取得urllist內每個網址
    import requests
    from bs4 import BeautifulSoup
    proxies = {
    'http': 'http://118.161.47.160:80',                   #換proxies,以備不時之需
    'https': 'http://118.161.47.160:80'
    }
    rs = requests.session()
#    res =rs.get(url,headers = headers, proxies = proxies)         #換proxies之request
    res =rs.get(url,headers = headers)
    res.encoding = 'utf-8'
    return BeautifulSoup(res.text,'html.parser')
num = 'num{}'
countReview = 1
with io.open('專題背包客棧國內各家旅行社評價正式版含翻頁2.txt', 'w',encoding='UTF-8') as f:       #將資料輸入檔案
    try:
        for urlele in urllist:
            url = urlform + urlele                                             #先進入"背包客棧"的評論頁面第一頁
            print url
            f.write(url.decode('utf-8')+'\n')
            soup =geturl(url)
            count = 0
            for ele in soup.select('.alt1 a'):

#                m = re.search('showthread.php?',ele['href'])                      #用此regular_expression抓網址會出現兩條評論內容重複的網址
                m = re.search('showthread.php?',ele['href'])                      #用這條regular_expression,就只抓出/showthread.php?t=6~7位數韓標題之網址
                if (m is not None) and (len(ele['href'].split('=')) < 3):               #觀察發現,網址有showthread.php?才真正有旅客評論
                    tempDic = {}
                    print ele['href']                                              #抓取評論頁面每一條評論href下的相對網址
                    f.write(ele['href'].decode('utf-8')+'\n')
                    print urlform + '/' + ele['href']                              #將有真正有旅客留言的網址做出來,製造出評論頁面每一條評論的完整網址
                    tempDic['href' + num.format(count)] = urlform + '/' + ele['href']     #將每一條評論的網址灌入dict
                    f.write((urlform + '/' + ele['href']).decode('utf-8')+'\n')
                    print ele.text
                    f.write(ele.text+'\n')
                    tempDic['title' + num.format(count)] = ele.text                       #將每一條評論的"標題"灌入dict
                    print ('=============================')
                    soupthread =geturl(urlform + '/' + ele['href'])
                    reviewDic = {}
                    n = 'n{}'
                    c = 1
                    for element in soupthread.select('.vb_postbit'):
                        print ('----------------------------')
                        print element.text
                        f.write(element.text+'\n')
                        reviewDic['review' + n.format(c)] = element.text                  #將每一條評論的"內容"灌入dict
                        print ('----------------------------')
                        c += 1
                    tempDic['評論'] = reviewDic
                    count += 1

                    print ('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
                    f.write(u'+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
                    projectList.append(tempDic)

        #翻到第二頁之後
            countpage = 2                                                           #因為評價論壇共"ˊ60"頁,從第2頁以後的url需要count的資訊
       #    print len(soup.select('.vbmenu_control'))
#            print ('##########################')
            p = re.search('\d{2}',soup.select('.vbmenu_control')[14].text)      #用regular express萃取出"共有多少頁"的資訊
#            print p.group(0)
            urlele = urlele + '&page='+ str(count)                              #評價論壇第二頁之後的網址有加上&page=
            url = urlform + urlele
            print url
            f.write(url.decode('utf-8')+'\n')
            soup =geturl(url)

            while(countpage <= int(p.group(0))):                                  #設定翻頁資訊
                for ele in soup.select('.alt1 a'):

                    m = re.search('showthread.php?',ele['href'])                      #用這條regular_expression,就只抓出/showthread.php?t=6~7位數韓標題之網址
                    if (m is not None) and (len(ele['href'].split('=')) < 3):               #觀察發現,網址有showthread.php?才真正有旅客評論
                        tempDic = {}
                        print ele['href']                                              #抓取評論頁面每一條評論href下的相對網址
                        f.write(ele['href'].decode('utf-8')+'\n')
                        print urlform + '/' + ele['href']                              #將有真正有旅客留言的網址做出來,製造出評論頁面每一條評論的完整網址
                        tempDic['href' + num.format(count)] = urlform + '/' + ele['href']     #將每一條評論的網址灌入dict
                        f.write((urlform + '/' + ele['href']).decode('utf-8')+'\n')
                        print ele.text
                        f.write(ele.text+'\n')
                        tempDic['title' + num.format(count)] = ele.text                       #將每一條評論的"標題"灌入dict
                        print ('=============================')
                        soupthread =geturl(urlform + '/' + ele['href'])
                        reviewDic = {}
                        n = 'n{}'
                        c = 1
                        for element in soupthread.select('.vb_postbit'):
                            print ('----------------------------')
                            print element.text
                            f.write(element.text+'\n')
                            reviewDic['review' + n.format(c)] = element.text                  #將每一條評論的"內容"灌入dict
                            print ('----------------------------')
                            c += 1
                        tempDic['評論'] = reviewDic
                        count += 1

                        print ('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
                        f.write(u'+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
                        projectList.append(tempDic)


                countpage += 1
                urlele = urlele.split('&')[0] + '&' + urlele.split('&')[1] + '&page=' + str(countpage)      #做出翻頁(第二頁之後)之網址
                url = urlform + urlele
                print url
                soup =geturl(url)

#                        projectList.append(tempDic)

#                countpage += 1
#                urlele = urlele.split('&')[0] + '&' + urlele.split('&')[1] + '&page=' + str(countpage)      #做出翻頁(第二頁之後)之網址
#                url = urlform + urlele
#                print url
#                soup =geturl(url)

#            projectList.append(tempDic)
            print('**************************************************************')

    except requests.exceptions.ConnectionError:
        print requests.exceptions.ConnectionError
    #    print 'we have crawer at leat'+ (count-1) +'pages'
    finally:
        for ele in projectList:
            for key in sorted(ele):
                print key,ele[key]
        print ('#############################################################')

f.close()

import json
from json import load
with open('專題背包客棧國內各家旅行社評價正式版含翻頁2.json', 'w') as f:                               #轉成.json檔
    json.dump(projectList, f)




