# -*- coding: utf-8 -*-
import io
import re

headers ={
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate, sdch, br',
'Accept-Language':'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4',
'Cache-Control':'max-age=0',
'Connection':'keep-alive',
# 'Cookie':'TAUnique=%1%enc%3AUl3cwI1xc%2FTwsb385vMtATZhvkrLn01BufRn5N1xwqg1zuHpUDBstg%3D%3D; __gads=ID=fd97053f079cb8ac:T=1464841916:S=ALNI_MbJojMYnpBrawgR9y_4NEBJNG0Deg; TAAuth2=%1%3%3A6417c520b203ebad2e7422a341efb8ec%3AAFrize7eFxrMHZAhEjQ1R6vp71NrngMb1kZQ3ZHBER7%2BN2hNipWsPSAotWXX1pbZ3xAHG1ZhXd0Q3UDH3TzzYTmGk2FYmBszCn%2BiADd8xOGwqaNYImrGQWkIEdU8I4igmlETEN8lGHVWt0YF2FusTjfhrgai7bTZV2SXUj07qHB1OY26BlgFXkCnN8%2FO9B4zK2V1tX3NP64xGnqBi0%2B%2FTghtDYYyI%2BF%2BFoXG863eckIm; TASSK=enc%3AY%2B8faEoGrSzZeKuLBMQl4ux5o9FsuevcHHI2z1PzCTf%2BNEvcfA5zo4lPySHGFHQKS7ktjdRhPq0%3D; ServerPool=C; TART=%1%enc%3A1uuQrU3JlwiuwCxmUqQISTwnGUaZsbIXPRFxT%2BYmI1nv5%2FKLFv4Gy6S2YdCGqRrgjcUVV%2FjQ5bY%3D; TATravelInfo=V2*AC.TPE*A.2*MG.-1*HP.2*FL.3*RVL.310298_168l579136_168l1811698_168l307253_168l298102_169l298143_169l298129_169l1130965_169l1127347_169l1009214_169l670212_169l1868572_169l294232_171l298156_171l298184_171*RS.1; CM=%1%HanaPersist%2C%2C-1%7Cpu_vr2%2C%2C-1%7Ct4b-pc%2C%2C-1%7CHanaSession%2C%2C-1%7CRCPers%2C%2C-1%7CWShadeSeen%2C%2C-1%7Cpu_vr1%2C%2C-1%7CFtrPers%2C%2C-1%7CHomeASess%2C5%2C-1%7CAWPUPers%2C%2C-1%7Ccatchsess%2C%2C-1%7Cbrandsess%2C%2C-1%7CCpmPopunder_1%2C3%2C1466428517%7CCCSess%2C%2C-1%7CCpmPopunder_2%2C3%2C-1%7Csesssticker%2C%2C-1%7C%24%2C%2C-1%7Ct4b-sc%2C%2C-1%7CMC_IB_UPSELL_IB_LOGOS2%2C%2C-1%7Cb2bmcpers%2C%2C-1%7CMC_IB_UPSELL_IB_LOGOS%2C%2C-1%7Csess_rev%2C6%2C-1%7Csessamex%2C%2C-1%7CSaveFtrPers%2C%2C-1%7Cpers_rev%2C%2C-1%7CMetaFtrSess%2C%2C-1%7CRBAPers%2C%2C-1%7CWAR_RESTAURANT_FOOTER_PERSISTANT%2C%2C-1%7CFtrSess%2C%2C-1%7CHomeAPers%2C%2C-1%7C+r_lf_1%2C%2C-1%7CRCSess%2C%2C-1%7C+r_lf_2%2C%2C-1%7Ccatchpers%2C3%2C1466498660%7CAWPUSess%2C%2C-1%7Cvr_npu2%2C%2C-1%7Csh%2C%2C-1%7CLastPopunderId%2C137-1859-null%2C-1%7Cpssamex%2C%2C-1%7C2016sticksess%2C%2C-1%7Cvr_npu1%2C%2C-1%7CCCPers%2C%2C-1%7CWAR_RESTAURANT_FOOTER_SESSION%2C%2C-1%7Cbrandpers%2C%2C-1%7Cb2bmcsess%2C%2C-1%7C2016stickpers%2C%2C-1%7CWarPopunder_Session%2C%2C-1%7CWarPopunder_Persist%2C%2C-1%7Cr_ta_2%2C%2C-1%7Cr_ta_1%2C%2C-1%7CSaveFtrSess%2C%2C-1%7CRBASess%2C%2C-1%7Cperssticker%2C%2C-1%7CMetaFtrPers%2C%2C-1%7C; TAReturnTo=%1%%2FAttractions-g298184-Activities-Tokyo_Tokyo_Prefecture_Kanto.html; roybatty=AFlfq3YnJt0%2FhokLLbs7MGW9EajHmpzavhHXcgH0OJYd%2F27aIpXrweDI9KOCWYvzmIJ9xuVfLqF3tqZIXBFEFpCo6jNKJhjkKGQmuP%2BuCYzu8w3%2FGI3VpjTNUA7H3Cz9rrtUeraaj41sz0rjr1ygWP714QfOL01uoKIKcUKRp64V%2C1; _em_vt=b10fed371c83b8b178c065d0383e574fb6bcd65735-2506595557669ae7; _em_v=12e65222d9a739f6e1b12098ba2057669a2791fc27-7233707257669ae7; TASession=%1%V2ID.EF6C6DFF759A960D5A7FC4E9269B5E85*SQ.58*MC.10568*LS.PageMoniker*GR.45*TCPAR.95*TBR.0*EXEX.58*ABTR.29*PPRP.61*PHTB.43*FS.2*CPU.53*HS.popularity*ES.popularity*AS.popularity*DS.5*SAS.popularity*FPS.oldFirst*TS.4704D895A3C3623D8925D3C0BAA24E20*FA.1*DF.0*LR.https%3A%2F%2Fwww%5C.google%5C.com%5C.tw%2F*LP.%2F*FBH.2*MS.-1*RMS.-1*FLO.298184*TRA.true*LD.298184; TAUD=LA-1466313368439-1*LG-28752581-2.1.F.*LD-28752583-.....; NPID=',
'Host':'www.tripadvisor.com.tw',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',                                                                        #這是主頁面須載入之header,是DOC靜態文件,用get方法取得
}

projectList = []
urlform = 'https://www.tripadvisor.com.tw'         #下面url所共有的表頭網址,每個在urllist上的網址代表每個地區
urllist = ['/Attractions-g298184-Activities-c47-Tokyo_Tokyo_Prefecture_Kanto.html' ,            #東京都觀光網頁
           '/Attractions-g298564-Activities-c47-Kyoto_Kyoto_Prefecture_Kinki.html',                #京都觀光網頁
           '/Attractions-g298566-Activities-c47-Osaka_Osaka_Prefecture_Kinki.html',                #大阪觀光網頁
           '/Attractions-g298562-Activities-c47-Kobe_Hyogo_Prefecture_Kinki.html'                  #神戶觀光網頁
           ]

#tempDic = {u'景點與地標':'',u'自然與公園':'',u'購物':'',u'博物館':'',u'演唱會和表演':'',u'遊覽':'',u'戶外活動':'',u'動物園與水族館':'',u'飲食':'',u'休閒與娛樂':'',u'水上樂園與遊樂場':'',u'旅客資源':'',u'課程活動及工作仿':'',u'交通':'',u'spa與養生':'',u'夜生活':'',u'搭船遊覽與水上活動':'',u'活動':'',u'賭場與博弈':''}  #創一個Dictionary
def geturl(url):                                          #這函式是要自動化取得urllist內每個網址
    import requests
    from bs4 import BeautifulSoup
    rs = requests.session()
    res =rs.get(url,headers = headers)
    res.encoding = 'utf-8'
    return BeautifulSoup(res.text,'html.parser')

def getReviews(ele):                                       #這函式是要取得"該頁面下"的"每一個飯店"的旅客評論
    url_TourReviews = ele.select('a')[0]['href']          #此"旅客評論"網頁資訊藏在TripAdvisor該飯店的'a'標籤下
    urlform_TourReviews = urlform + url_TourReviews
    soupReview = geturl(urlform_TourReviews)              #利用函式geturl將個別飯店的"旅客評論"網址帶入,這是點選TripAdvisor該飯店所額外產生的網頁
    date ='date{}'
    countRivews = 0
    reviewPageNumber = 1
    or1 = 'or{}'
    EachDayCommentDic = {}
    kindnum = 'n{}'
    for reviews in soupReview.select('.innerBubble')[0:2]:            #先直接進行第一頁的評論
        countRivews += 1
        if len(reviews.select('.entry')) > 0:
#            EachDayCommentDic['觀光景點與景點類型']=tourDic['觀光景點'] +':'+ tourDic['景點類型']
            kd = 1
            EachDayCommentDic['觀光景點'] = tourDic['觀光景點']
            for key in tourDic['景點類型']:
                EachDayCommentDic['景點類型'+ kindnum.format(kd)] = tourDic['景點類型'][key]
                kd += 1
#                tourDic['景點類型'][key] + '\n'
            EachDayCommentDic[date.format(countRivews)] = reviews.select('.ratingDate')[0].text + ':' + reviews.select('.entry')[0].select('p')[0].text
            print EachDayCommentDic[date.format(countRivews)]
            f.write('\n'+ EachDayCommentDic[date.format(countRivews)]+'\n')                         #把這個景點之評論首頁抓下來
            f.write(u'------------------------------------------------')

#    url_TourReviews =  url_TourReviews.split('-')[0]+'-'+url_TourReviews.split('-')[1]+'-'+url_TourReviews.split('-')[2]+'-'+ or1.format(10)+ '-' +url_TourReviews.split('-')[3]+ '-' +url_TourReviews.split('-')[4]+ '-' +url_TourReviews.split('-')[5]

#    if (len(soupReview.select('.pageNumbers')) > 0):
#        while(reviewPageNumber < len(soupReview.select('.pageNumbers')[0].select('a'))):  #先收集出現頁面(第一頁)的評論資料, 因為"第一頁"的標籤是'span'而第二頁之後的標籤是'a'
#            urlform_TourReviews = urlform + url_TourReviews
#            soupReview = geturl(urlform_TourReviews)              #利用函式geturl將個別飯店的"旅客評論"網址帶入,這是點選TripAdvisor該飯店所額外產生的網頁

#            for reviews in soupReview.select('.innerBubble'):
#                countRivews += 1

#                if len(reviews.select('.entry')) > 0:               #怕產生error_message,所以先給條件
#                    EachDayCommentDic['觀光景點與景點類型']=tourDic['觀光景點'] +':'+ tourDic['景點類型']
#                    EachDayCommentDic[date.format(countRivews)] = reviews.select('.ratingDate')[0].text + ':' + reviews.select('.entry')[0].select('p')[0].text
#                    print EachDayCommentDic[date.format(countRivews)]

#            reviewPageNumber += 1
#            cout = 10*reviewPageNumber                  #這一行是因為評論網頁網址的規則,每翻一頁加10
#            print reviewPageNumber
#            print ('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
#            url_TourReviews =  url_TourReviews.split('-')[0]+'-'+url_TourReviews.split('-')[1]+'-'+url_TourReviews.split('-')[2]+'-'+ or1.format(cout)+ '-' +url_TourReviews.split('-')[4]+ '-' +url_TourReviews.split('-')[5]+ '-' +url_TourReviews.split('-')[6]
            #上面那一行(比較難懂),是指定"新的"url_HotelReviews,可以看到在split[2]和split[4]中間塞入or1.format(cout)以製造新的網址給while下一行的url_HotelReviews使用
            #直到整個while迴圈跑完, 即or1.format(cout)隨cout不同產生不同的評論網頁(url)
#            print ('!!!!!!!!!!!!!!!!!!!!!!!!')
        tourDic['景點評論'] = EachDayCommentDic
oa = 'oa{}'
num = 'num{}'
count = 1
with io.open('TripAdvistor東京京都大阪神戶觀光活動細項目條列與旅遊評論字典檔輕量正式新版.txt', 'w',encoding='UTF-8') as f:       #將資料輸入檔案
    for urlele in urllist:
        placeDic ={}
        tempDic = {}
        f.write('\n'+urlele.split('-')[4].split('_')[0]+ u'地區觀光活動有:'+'\n')         #列出觀光地點,如:東京或京都等
        f.write(u'*******************')
        urlform_url = urlform + urlele
        soup =geturl(urlform_url)
        print urlform_url
        tourDic = {}
        countpoint = 1
        kindnum = 'n{}'

        for ele in soup.select('.wrap.al_border.attraction_element'):
    #        tempDic['觀光景點'+num.format(countpoint)] = ele.text
            tourDic['觀光景點']= ele.select('.entry')[0].select('.property_title')[0].text
            print tourDic['觀光景點']
            f.write('\n'+tourDic['觀光景點']+u'的景觀類型是:' +'\n')
            kindDic ={}
            kd = 1
            for kindele in ele.select('.p13n_reasoning_v2')[0].select('.noTagImg'):    #一個觀光景點可以有多個景點類型
                kindDic['景點類型'+ kindnum.format(kd)] = kindele.text
                print (kindDic['景點類型'+ kindnum.format(kd)]+'\n')
                f.write(kindDic['景點類型'+ kindnum.format(kd)]+'\n')
                print ('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
                kd += 1
            tourDic['景點類型'] = kindDic
   #         tourDic['景點類型'] = ele.select('.p13n_reasoning_v2')[0].select('.noTagImg')[0].text

#            for key in tourDic['景點類型']:
#                print tourDic['景點類型'][key] +'\n'
#                f.write(tourDic['景點類型'][key]+'\n')
    #        f.write(u'============================================================')
#            print ele.select('.p13n_reasoning_v2')[0].select('.noTagImg')[0].text

            print ele.select('a')[0]['href']
            print urlform + ele.select('a')[0]['href']                    #得到了旅客評論的頁面
            getReviews(ele)                                               #寫一個取得旅客評論的函式(平均每個景點有數千筆以上,需翻頁)
    #        tempDic[num.format(countpoint)] = tourDic['景點評論']          #包含了getReviews內EachDayCommentDic['觀光景點與景點類型']當成disc的第一項與其他分項代表旅客不同時間點的評論
            tempDic[ele.select('.entry')[0].select('.property_title')[0].text] = tourDic['景點評論']
            print ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            countpoint +=1                                      #計算該地區(東京都)的景點數


        print  countpoint
        print ('**********************************')
        #print soup.select('.filter_count')[0].text             抓取分頁頁數的資訊
        m = re.search(u'([0-9,]+)',soup.select('.filter_count')[0].text)     #運用regular expression去除左右括號
        print int(m.group(1))
        print ('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
        urlele = urlele.split('-')[0]+'-'+urlele.split('-')[1]+'-'+urlele.split('-')[2]+'-'+ urlele.split('-')[3]+ '-'+ oa.format(count*30) + '-'+urlele.split('-')[4]+'#ATTRACTION_LIST' #換到下一頁

        while(count <= int(m.group(1))/30):                   #細項所顯示項目之頁數(比方東京都有1202項,共41分頁)
            urlform_url = urlform + urlele
            soup =geturl(urlform_url)
            print urlform_url
            tourDic = {}
            kindnum = 'n{}'

            for ele in soup.select('.wrap.al_border.attraction_element'):
                tourDic['觀光景點']= ele.select('.entry')[0].select('.property_title')[0].text
    #            tempDic['觀光景點'+num.format(countpoint)] = ele.text
                print tourDic['觀光景點']
                f.write('\n'+tourDic['觀光景點']+u'的景觀類型是:' +'\n')
                kindDic = {}
                kd = 1
                for kindele in ele.select('.p13n_reasoning_v2')[0].select('.noTagImg'):    #一個觀光景點可以有多個景點類型
                    kindDic['景點類型'+ kindnum.format(kd)] = kindele.text
                    print (kindDic['景點類型'+ kindnum.format(kd)]+'\n')
                    f.write(kindDic['景點類型'+ kindnum.format(kd)]+'\n')
                    print ('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
                    kd += 1
                tourDic['景點類型'] = kindDic
    #            tourDic['景點類型'] = ele.select('.p13n_reasoning_v2')[0].select('.noTagImg')[0].text

    #            for key in tourDic['景點類型']:
    #                print tourDic['景點類型'][key] + '\n'
    #                f.write(tourDic['景點類型'][key]+'\n')
    #            f.write(u'============================================================')
    #            print ele.select('.p13n_reasoning_v2')[0].select('.noTagImg')[0].text
                print ele.select('a')[0]['href']
                print urlform + ele.select('a')[0]['href']                 #得到了旅客評論的頁面
                getReviews(ele)                                            #寫一個取得旅客評論的函式(平均每個景點有數千筆以上,需翻頁)
    #            tempDic[num.format(countpoint)] = tourDic['景點評論']         #包含了getReviews內EachDayCommentDic['觀光景點與景點類型']當成disc的第一項與其他分項代表旅客不同時間點的評論
                tempDic[ele.select('.entry')[0].select('.property_title')[0].text] = tourDic['景點評論']
                print ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                countpoint +=1


            urlele = urlele.split('-')[0]+'-'+urlele.split('-')[1]+'-'+urlele.split('-')[2]+'-'+ urlele.split('-')[3]+ '-'+ oa.format(count*30) + '-'+urlele.split('-')[5]+'#ATTRACTION_LIST'  #換到下一頁
            count += 1

        placeDic[urlele.split('-')[5].split('_')[0]] = tempDic                       #把整個關關景點再塞入日本地區, 如:東京,京都等
        ABC = placeDic.copy()                                                               #這一步藉由copy的動做新建一個物件,以防止相同key值其value植被覆蓋
        projectList.append(ABC)

        print('=========================================================')
f.close()
for ele in projectList:
    for key in sorted(ele):
        print key,ele[key]
print ('#############################################################')

import json
from json import load
with open('TripAdvistor東京京都大阪神戶觀光活動細項目條列與旅遊評論字典檔輕量正式新版.json', 'w') as f:                               #轉成.json檔
    json.dump(projectList, f)



