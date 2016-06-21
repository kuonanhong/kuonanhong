# -*- coding: utf-8 -*-
import re
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
tempDic = {}
def geturl(url):                                          #這函式是要自動化取得urllist內每個網址
    import requests
    from bs4 import BeautifulSoup
    rs = requests.session()
    res =rs.get(url,headers = headers)
    res.encoding = 'utf-8'
    return BeautifulSoup(res.text,'html.parser')
num = 'num{}'
countReview = 1
for urlele in urllist:
    url = urlform + urlele                                             #先進入"背包客棧"的評論頁面第一頁
    print url
    soup =geturl(url)
#    for ele in soup.select('.alt1 a'):
#        print ele['href']
    for ele in soup.select('.alt2 a'):                                 #在評論頁面第一頁,在標籤.alt2 a下取得旅客對各大旅行社的評論
        print ele['href']                                              #下開出的"連結"
        print urlform + '/' + ele['href']                              #將有真正有旅客留言的網址做出來
        soupthread =geturl(urlform + '/' + ele['href'])
        for ele in soupthread.select('.vb_postbit'):                   #在真正有旅客留言的網址下的標籤.vb_postbit取出旅客的"評論文字"
            print ele.text
            tempDic['旅客評論' + num.format(countReview)] = ele.text
            countReview += 1
            print ('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
    print('===================================')
    count = 2                                                           #因為評價論壇共"59"頁,從第2頁以後的url需要count的資訊
    m = re.search('\d{2}',soup.select('.vbmenu_control')[14].text)      #用regular express萃取出"共有多少頁"的資訊
    urlele = urlele + '&page='+ str(count)                              #評價論壇第二頁之後的網址有加上&page=
    url = urlform + urlele
    print url
    soup =geturl(url)

    while(count <= int(m.group(0))):                                    #int(m.group(0))代表有"59"頁(萃取出這可能變動的資訊)
#        for ele in soup.select('.alt1 a'):
#             print ele['href']
        for ele in soup.select('.alt2 a'):
            print ele['href']
            print urlform + '/' + ele['href']
            soupthread =geturl(urlform + '/' + ele['href'])
            for ele in soupthread.select('.vb_postbit'):
                print ele.text
                tempDic['旅客評論' + num.format(countReview)] = ele.text
                countReview += 1
                print ('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
        print ('===================================')
        count += 1
        urlele = urlele.split('&')[0] + '&' + urlele.split('&')[1] + '&page=' + str(count)      #做出翻頁(第二頁之後)之網址
        url = urlform + urlele
        print url
        soup =geturl(url)

    projectList.append(tempDic)
    print('**************************************************************')

for ele in projectList:
    for key in sorted(ele):
        print key,ele[key]
print ('#############################################################')

import json
from json import load
with open('專題背包客棧國內各家旅行社評價.json', 'w') as f:                               #轉成.json檔
    json.dump(projectList, f)



