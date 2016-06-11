# -*- coding: utf-8 -*-
import io
import re

headers ={                                                                            #這是主頁面須載入之header,是DOC靜態文件,用get方法取得
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate, sdch, br',
'Accept-Language':'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4',
'Cache-Control':'max-age=0',
'Connection':'keep-alive',
'Cookie':'TASSK=enc%3AOlceurmvp1NnkG7OOMKFKpNtfWg9azKUO2QNcxr4mL83vUy2dd0COeHSbyuF9mUhVtocHv%2BreUc%3D; TAUnique=%1%enc%3AUl3cwI1xc%2FTwsb385vMtATZhvkrLn01BufRn5N1xwqg1zuHpUDBstg%3D%3D; __gads=ID=fd97053f079cb8ac:T=1464841916:S=ALNI_MbJojMYnpBrawgR9y_4NEBJNG0Deg; TART=%1%enc%3A1uuQrU3JlwiuwCxmUqQISTwnGUaZsbIXPRFxT%2BYmI1nv5%2FKLFv4Gy6S2YdCGqRrgjcUVV%2FjQ5bY%3D; ServerPool=X; TATravelInfo=V2*AC.TPE*A.2*MG.-1*HP.2*FL.3*RVL.298190_157l294232_157l298156_157*RS.1; CM=%1%HanaPersist%2C%2C-1%7Cpu_vr2%2C%2C-1%7Ct4b-pc%2C%2C-1%7CHanaSession%2C%2C-1%7CRCPers%2C%2C-1%7CWShadeSeen%2C%2C-1%7Cpu_vr1%2C%2C-1%7CFtrPers%2C%2C-1%7CHomeASess%2C6%2C-1%7CAWPUPers%2C%2C-1%7Ccatchsess%2C5%2C-1%7Cbrandsess%2C%2C-1%7CCpmPopunder_1%2C2%2C1465225893%7CCCSess%2C%2C-1%7CCpmPopunder_2%2C2%2C-1%7Csesssticker%2C%2C-1%7C%24%2C%2C-1%7Ct4b-sc%2C%2C-1%7CMC_IB_UPSELL_IB_LOGOS2%2C%2C-1%7Cb2bmcpers%2C%2C-1%7CMC_IB_UPSELL_IB_LOGOS%2C%2C-1%7Csess_rev%2C%2C-1%7Csessamex%2C%2C-1%7Chac_ua_rd%2C%2C-1%7CSaveFtrPers%2C%2C-1%7Cpers_rev%2C%2C-1%7CMetaFtrSess%2C%2C-1%7CRBAPers%2C%2C-1%7CWAR_RESTAURANT_FOOTER_PERSISTANT%2C%2C-1%7CFtrSess%2C%2C-1%7CHomeAPers%2C%2C-1%7C+r_lf_1%2C%2C-1%7CRCSess%2C%2C-1%7C+r_lf_2%2C%2C-1%7Ccatchpers%2C3%2C1465739160%7CAWPUSess%2C%2C-1%7Cvr_npu2%2C%2C-1%7Csh%2C%2C-1%7CLastPopunderId%2C137-1859-null%2C-1%7Cpssamex%2C%2C-1%7C2016sticksess%2C%2C-1%7Cvr_npu1%2C%2C-1%7CCCPers%2C%2C-1%7CWAR_RESTAURANT_FOOTER_SESSION%2C%2C-1%7Cbrandpers%2C%2C-1%7Cb2bmcsess%2C%2C-1%7C2016stickpers%2C%2C-1%7CWarPopunder_Session%2C%2C-1%7CWarPopunder_Persist%2C%2C-1%7Cr_ta_2%2C%2C-1%7Cr_ta_1%2C%2C-1%7CSaveFtrSess%2C%2C-1%7CRBASess%2C%2C-1%7Cperssticker%2C%2C-1%7CMetaFtrPers%2C%2C-1%7C; TAReturnTo=%1%%2FHotels-g298156-Kanto-Hotels.html; roybatty=ANkZ4mziDsRuc7hyCgSDwMmfSdrye%2BqA59q6iYJqrHgwjrcHgF4nAkJ8BhXxJ9kJmc1hZ8s%2Btn7Y%2BorIbwcuX5%2BrDY%2BuzY3bqDWuB1G6mROlwYin2BRGDGf43EwXGYS4c3J7kfGlB0Y2qxnwYjq27bg3okXekFuZr4T7eB4MTJXV%2C1; _em_vt=910a223c8060ad19fab065d0383e574fb6bcd65735-2506595557544830; _em_v=21815a8c3e6f447a915c027f3ab657544104dfdfc9-1532233257544830; TASession=%1%V2ID.8C2E47435135022C640979EBE075F117*SQ.55*MC.13999*LS.PageMoniker*GR.36*TCPAR.39*TBR.80*EXEX.68*ABTR.26*PPRP.42*PHTB.44*FS.98*CPU.85*HS.popularity*ES.popularity*AS.popularity*DS.5*SAS.popularity*FPS.oldFirst*FA.1*DF.0*LR.https%3A%2F%2Fwww%5C.google%5C.com%5C.tw%2F*LP.%2F-a_supli%5C.-a_supti%5C.aud__2D__90391767427%253Akwd__2D__119671122-a_supdv%5C.c-m13999-a_supsc%5C.s-a_supap%5C.1t1-a_suplp%5C.1012817-a_supbk%5C.1-a_supai%5C.35263108371-a_supci%5C.694799784-a_supnt%5C.g*FBH.2*MS.-1*RMS.-1*TRA.true*LD.298156*BG.298156*BT.hto1wc; TAUD=LA-1465134358056-1*LG-6939889-2.1.F*LD-6939891-.....; NPID=',
'Host':'www.tripadvisor.com.tw',
'Referer':'https://www.tripadvisor.com.tw/Tourism-g298156-Kanto-Vacations.html',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
}

headershotel ={                                                                       #這是經過翻頁動作新增post方法所用的header,是XHR文件,在執行翻頁時才會產生
'Accept':'text/javascript, text/html, application/xml, text/xml, */*',
'Accept-Encoding':'gzip, deflate, br',
'Accept-Language':'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4',
'Connection':'keep-alive',
'Content-Length':'174',
'Content-type':'application/x-www-form-urlencoded; charset=UTF-8',
#'Cookie':'TASSK=enc%3AOlceurmvp1NnkG7OOMKFKpNtfWg9azKUO2QNcxr4mL83vUy2dd0COeHSbyuF9mUhVtocHv%2BreUc%3D; TAUnique=%1%enc%3AUl3cwI1xc%2FTwsb385vMtATZhvkrLn01BufRn5N1xwqg1zuHpUDBstg%3D%3D; __gads=ID=fd97053f079cb8ac:T=1464841916:S=ALNI_MbJojMYnpBrawgR9y_4NEBJNG0Deg; TAAuth2=%1%3%3A6417c520b203ebad2e7422a341efb8ec%3AAFrize7eFxrMHZAhEjQ1R6vp71NrngMb1kZQ3ZHBER7%2BN2hNipWsPSAotWXX1pbZ3xAHG1ZhXd0Q3UDH3TzzYTmGk2FYmBszCn%2BiADd8xOGwqaNYImrGQWkIEdU8I4igmlETEN8lGHVWt0YF2FusTjfhrgai7bTZV2SXUj07qHB1OY26BlgFXkCnN8%2FO9B4zK2V1tX3NP64xGnqBi0%2B%2FTghtDYYyI%2BF%2BFoXG863eckIm; TART=%1%enc%3A1uuQrU3JlwiuwCxmUqQISTwnGUaZsbIXPRFxT%2BYmI1nv5%2FKLFv4Gy6S2YdCGqRrgjcUVV%2FjQ5bY%3D; ServerPool=X; TATravelInfo=V2*AC.TPE*A.2*MG.-1*HP.2*FL.3*RVL.298190_157l294232_158l594517_158l293913_159l579136_159l635211_160l6883207_160l301930_160l4050438_160l1475716_160l310298_161l302387_161l7002465_161l307399_161l298156_161*RS.1; roybatty=AMndnPP%2FV6VLKcBduLmSmxBBduxLRffwL3MN3SjgzRYrmTv2AkpbfJhadLDaMeYTJKJ6rvbHSS5XgAog46f32J6ERU2rCroMTiyEtTbxTuJ2PutVjN5GN4N7P0p2xw1DuVIxJuBA7RAmFi1ODto%2FfdjIjlvbggbyoNlqLwjxWPXy%2C1; _em_vt=6d0d06058a669d44aa5065d0383e574fb6bcd65735-250659555759712f; _em_v=a59bb2afc14cdef5044e46ea29285759704a0e1399-196486695759712f; CM=%1%HanaPersist%2C%2C-1%7Cpu_vr2%2C%2C-1%7Ct4b-pc%2C%2C-1%7CHanaSession%2C%2C-1%7CRCPers%2C%2C-1%7CWShadeSeen%2C%2C-1%7Cpu_vr1%2C%2C-1%7CFtrPers%2C%2C-1%7CHomeASess%2C3%2C-1%7CAWPUPers%2C%2C-1%7Ccatchsess%2C%2C-1%7Cbrandsess%2C%2C-1%7CCpmPopunder_1%2C17%2C1465565869%7CCCSess%2C%2C-1%7CCpmPopunder_2%2C9%2C-1%7Csesssticker%2C%2C-1%7C%24%2C%2C-1%7Ct4b-sc%2C%2C-1%7CMC_IB_UPSELL_IB_LOGOS2%2C%2C-1%7Cb2bmcpers%2C%2C-1%7CMC_IB_UPSELL_IB_LOGOS%2C%2C-1%7Csess_rev%2C11%2C-1%7Csessamex%2C%2C-1%7Chac_ua_rd%2C%2C-1%7CSaveFtrPers%2C%2C-1%7Cpers_rev%2C%2C-1%7CMetaFtrSess%2C%2C-1%7CRBAPers%2C%2C-1%7CWAR_RESTAURANT_FOOTER_PERSISTANT%2C%2C-1%7CFtrSess%2C%2C-1%7CHomeAPers%2C%2C-1%7C+r_lf_1%2C%2C-1%7CRCSess%2C%2C-1%7C+r_lf_2%2C%2C-1%7Ccatchpers%2C3%2C1465739160%7CAWPUSess%2C%2C-1%7Cvr_npu2%2C%2C-1%7Csh%2C%2C-1%7CLastPopunderId%2C137-1859-null%2C-1%7Cpssamex%2C%2C-1%7C2016sticksess%2C%2C-1%7Cvr_npu1%2C%2C-1%7CCCPers%2C%2C-1%7Cbrandpers%2C3%2C1465973723%7CWAR_RESTAURANT_FOOTER_SESSION%2C%2C-1%7Cb2bmcsess%2C%2C-1%7C2016stickpers%2C%2C-1%7CWarPopunder_Session%2C%2C-1%7CWarPopunder_Persist%2C%2C-1%7Cr_ta_2%2C%2C-1%7Cr_ta_1%2C%2C-1%7CSaveFtrSess%2C%2C-1%7CRBASess%2C%2C-1%7Cperssticker%2C%2C-1%7CMetaFtrPers%2C%2C-1%7C; TAReturnTo=%1%%2FHotels%3Frooms%3D1%26searchAll%3Dfalse%26adults%3D2%26pageSize%3D%26hs%3D%26seen%3D0%26o%3Da30%26g%3D298156%26displayedSortOrder%3Dpopularity%26sequence%3D1%26refineForm%3Dtrue%26rad%3D0%26requestingServlet%3DHotels%26dateBumped%3DNONE; NPID=; TASession=%1%V2ID.E9A4700629A5FB1FA8350F293ADF359D*SQ.144*MC.10568*LS.SavesAjax*GR.19*TCPAR.19*TBR.80*EXEX.19*ABTR.60*PPRP.85*PHTB.9*FS.68*CPU.64*HS.popularity*ES.popularity*AS.popularity*DS.5*SAS.popularity*FPS.oldFirst*TS.4704D895A3C3623D8925D3C0BAA24E20*LF.zhTW*FA.1*DF.0*LR.https%3A%2F%2Fwww%5C.google%5C.com%5C.tw%2F*LP.%2F*FBH.2*MS.-1*RMS.-1*TRA.true*LD.298156*BG.298156*BT.htn3t4; TAUD=LA-1465449651151-1*LG-29844798-2.1.F*LD-29844800-.....',
'Host':'www.tripadvisor.com.tw',
'Origin':'https://www.tripadvisor.com.tw',
'Referer':'',                                              #因為這是動態產生的頁面, 'Referer'的值在後面動態塞入
#'Referer':'https://www.tripadvisor.com.tw/Hotels-g298156-Kanto-Hotels.html',   #這是原來頁面所給, 動態產生方面被我找到規則
'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36',
'X-Puid':'V1lxLAokK3EAAKl7D5wAAAA4',
'X-Requested-With':'XMLHttpRequest'
}
#經觀察每個Hotel頁面的Cookie好像都不同,由於不傷大雅,故將它註解掉
payload ={                                                #這是經過翻頁動作新增post方法所用的data,是XHR文件
'seen':'0',
'sequence':'1',
'geo':'298156',
'adults':'2',
'rooms':'1',
'searchAll':'false',
'requestingServlet':'Hotels',
'refineForm':'true',
'hs':'',
#'o':'a3600',     #原來參考第一頁Hotel是a0,第二頁Hotel是a30,....,for 關東地區(Kanto)其Hotel是a3600,因為共121頁,一頁有30個餐廳
 'o':'',          #但我們是隨地區不同改變payload的形式.但每頁30間餐廳還是固定的
'pageSize':'',
'rad':'0',
'dateBumped':'NONE',
'displayedSortOrder':'popularity'
}
projectList = []
urlform = 'https://www.tripadvisor.com.tw'         #下面url所共有的表頭網址,每個在urllist上的網址代表每個地區
urlHotels = 'https://www.tripadvisor.com.tw/Hotels'
urllist = [
           '/Hotels-g298156-Kanto-Hotels.html','/Hotels-g298189-Kinki-Hotels.html',\
           '/Hotels-g298237-Tohoku-Hotels.html','/Hotels-g298228-Shikoku-Hotels.html',\
           '/Hotels-g298143-Hokkaido-Hotels.html','/Hotels-g298205-Kyushu_Okinawa-Hotels.html',\
           '/Hotels-g298102-Chubu-Hotels.html','/Hotels-g298129-Chugoku-Hotels.html'
           ]
#Kanto:關東地區;Kinki:近畿地區;Tohoku:東北地區;Shikoku:四國;Hokkaido:北海道;
#Kyushu_Okinawa:九州沖繩地區;Chubu:中部地區;Chugoku:中國地方

tempDic = {'agency':'','area':'','hotel':'','hotel_comments':''}  #創一個Dictionary
tempDic['agency'] = 'TripAdvisor飯店評論'                              #將旅社姓名塞入key是agency的tempDic
date = 'date{}'
comment = 'comment{}'
hotel = 'hotel{}'                                                          #創造此projectList的目的是最後要將結果以appendix的方式加入此projectList
def geturl(url):                                          #這函式是要自動化取得urllist內每個網址
    import requests
    from bs4 import BeautifulSoup
    res =requests.get(url,headers = headers)
    res.encoding = 'utf-8'
    return BeautifulSoup(res.text,'html.parser')

def geturlpost(url):
    import requests
    from bs4 import BeautifulSoup
    rs = requests.session()                 #記錄Cookie,但好像是多餘的
    headershotel['Referer'] = urlform_url
    res =rs.post(url,headers = headershotel, data= payload)
    res.encoding = 'utf-8'
    return BeautifulSoup(res.text,'html.parser')

def getReviews(ele):                                       #這函式是要取得"該頁面下"的"每一個飯店"的旅客評論
    url_HotelReviews = ele.select('a')[0]['href']          #此"旅客評論"網頁資訊藏在TripAdvisor該飯店的'a'標籤下

    urlform_HotelReviews = urlform + url_HotelReviews
    soupReview = geturl(urlform_HotelReviews)              #利用函式geturl將個別飯店的"旅客評論"網址帶入,這是點選TripAdvisor該飯店所額外產生的網頁
    countRivews = 0
    reviewPageNumber = 1
    data_page_number = 'data_page_number{}'
    reviewPageDic = {}
    or1 = 'or{}'
    reviewDic = {}                               #先造新字典reviewDic,

    for reviews in soupReview.select('.innerBubble'):            #先直接進行第一頁的評論
        countRivews += 1
        if len(reviews.select('.entry')) > 0:
            reviewDic[date.format(countRivews)] = reviews.select('.ratingDate')[0].text
            print reviewDic[date.format(countRivews)]
            f.write(reviewDic[date.format(countRivews)]+'/n')
            reviewDic[comment.format(countRivews)] = reviews.select('.entry')[0].select('p')[0].text
            print reviewDic[comment.format(countRivews)]
            f.write(reviewDic[comment.format(countRivews)])
#    reviewPageDic[data_page_number.format(reviewPageNumber)] = reviewDic     #將此地區這個特定餐廳第一頁資訊塞成reviewPageDic[data_page_number1]

    print u'這是'+ tempDic['hotel'] + u'第1頁評論結束'
    f.write(u'這是'+ tempDic['hotel'] + u'第1頁評論結束'+'/n')
    url_HotelReviews =  url_HotelReviews.split('-')[0]+'-'+url_HotelReviews.split('-')[1]+'-'+url_HotelReviews.split('-')[2]+'-'+ or1.format(10)+ '-' +url_HotelReviews.split('-')[3]+ '-' +url_HotelReviews.split('-')[4]+ '-' +url_HotelReviews.split('-')[5]

    if (len(soupReview.select('.pageNumbers')) > 0):
        while(reviewPageNumber < len(soupReview.select('.pageNumbers')[0].select('a'))):  #先收集出現頁面(第一頁)的評論資料, 因為"第一頁"的標籤是'span'而第二頁之後的標籤是'a'
            urlform_HotelReviews = urlform + url_HotelReviews
            soupReview = geturl(urlform_HotelReviews)              #利用函式geturl將個別飯店的"旅客評論"網址帶入,這是點選TripAdvisor該飯店所額外產生的網頁

            for reviews in soupReview.select('.innerBubble'):
                countRivews += 1

                if len(reviews.select('.entry')) > 0:               #怕產生error_message,所以先給條件
                    reviewDic[date.format(countRivews)] = reviews.select('.ratingDate')[0].text
                    print reviewDic[date.format(countRivews)]
                    f.write(reviewDic[date.format(countRivews)]+'/n')
                    reviewDic[comment.format(countRivews)] = reviews.select('.entry')[0].select('p')[0].text
                    print reviewDic[comment.format(countRivews)]
                    f.write(reviewDic[comment.format(countRivews)]+'/n')
            reviewPageNumber += 1
            cout = 10*reviewPageNumber                  #這一行是因為評論網頁網址的規則,每翻一頁加10
            print u'這是' + tempDic['hotel'] + u'第' +  str(reviewPageNumber) + u'頁的評論結束'
            f.write(u'這是' + tempDic['hotel'] + u'第' +  str(reviewPageNumber)  + u'頁的評論結束'+'/n')
            url_HotelReviews =  url_HotelReviews.split('-')[0]+'-'+url_HotelReviews.split('-')[1]+'-'+url_HotelReviews.split('-')[2]+'-'+ or1.format(cout)+ '-' +url_HotelReviews.split('-')[4]+ '-' +url_HotelReviews.split('-')[5]+ '-' +url_HotelReviews.split('-')[6]
            #上面那一行(比較難懂),是指定"新的"url_HotelReviews,可以看到在split[2]和split[4]中間塞入or1.format(cout)以製造新的網址給while下一行的url_HotelReviews使用
            #直到整個while迴圈跑完, 即or1.format(cout)隨cout不同產生不同的評論網頁(url)
#            reviewPageDic[data_page_number.format(reviewPageNumber)] = reviewDic     #將此地區這個特定餐廳第一頁資訊塞成reviewPageDic[data_page_number n]

        tempDic['hotel_comments'] = reviewDic                  #將此地區這個特定餐廳所有評論資訊塞給tempDic['hotel_comments']
        print tempDic['hotel']+u'總計有'+str(countRivews)+u'則評論提供參考'
        print ('============================================================================================================================================')
        f.write(u'==============================================================================================================================================')

def getData2():
#    tempDic['hotel'] = soup2.select('.listing_title')[0].select('.property_title')[0].text
    RestantDic[hotel.format(countRest+1)] = soup2.select('.listing_title')[0].select('.property_title')[0].text
    print RestantDic[hotel.format(countRest+1)]                                     #印出tempDic['hotel']的值
    f.write(RestantDic[hotel.format(countRest+1)]+'/n')
    getReviews(soup2.select('.listing_title')[0])

with io.open('TripAdvisor飯店評論.txt', 'w',encoding='UTF-8') as f:     #將資料輸入檔案
    List = []                                                   #這個List的目的是用來判斷動態產生的餐廳數有無重複,方法是當動態產生的XHR文件若重複出現於List清單之中,則下方if條件不計次
    for urlele in urllist:
        urlform_url = urlform + urlele
        soup =geturl(urlform_url)
        tempDic['area'] = urlform_url.split('-')[2]            #將url出現的地名塞入tempDic['area']
        m = re.search(u'([0-9,]+)',soup.select('.tab_count')[0].text)       #取出這個地區總共有幾家旅行社的數目,用正規表達法取出(比方關東地區有3601家飯店)
        f.write(tempDic['area'] + u'這地區總共有'+ ''.join(m.group(1).split(',')) +u'家精選的旅行社'+'/n')
        print (tempDic['area'] + u'這地區總共有'+ ''.join(m.group(1).split(',')) +u'家精選的旅行社')
        countRest = 0
        while(countRest < int(''.join(m.group(1).split(',')))):      #循環列出這地區這些餐廳名稱與評論, 每個地區平均約有上千筆餐廳,並估計有上百萬筆全球來的評論
            soup2 = geturlpost(urlHotels)
            f.write(u'這是'+ tempDic['area']+u'地區第'+ str(countRest+1)+u'家餐廳'+'/n')
            print u'這是'+ tempDic['area']+u'地區第'+ str(countRest+1)+u'家餐廳'
            RestantDic={}                                            #先造一個空餐廳的子Dic,這是因為怕下方的getData2()中如果每次都將值塞入tempDic['hotel'],後面值會蓋住前面的值
            getData2()                                                   #這一步是關鍵, 即是取得所有的資料塞進Dic之中,並把資料顯示於螢幕上

#            if (tempDic['hotel'] not in List):                           #看動態更新的網頁其跳出的餐廳有無和之前重複
            if (RestantDic[hotel.format(countRest+1)] not in List):
                countRest = countRest +1                                 #不重複的餐廳才會進入if的條件之中,也才會計次(countRest+1)
                List.append(RestantDic[hotel.format(countRest)])                          #這一步藉由copy的動做新建一個物件,以防止相同key值其value植被覆蓋
                print RestantDic[hotel.format(countRest)] + u'此餐廳的所有評論結束'
                f.write(RestantDic[hotel.format(countRest)] + u'此餐廳的所有評論結束'+'/n')
            print ('--------------------------------------------------------------------------')
            f.write(u'--------------------------------------------------------------------------'+'/n')
        print tempDic['area'] +u'的區域所有餐廳評論結束'
        f.write(tempDic['area'] +u'的區域所有餐廳評論結束'+'/n')
        tempDic['hotel'] = RestantDic
        ABC = tempDic.copy()                                       #這一步藉由copy的動做新建一個物件,以防止相同key值其value植被覆蓋
        projectList.append(ABC)


for ele in projectList:
    for key in sorted(ele):
        print key,ele[key]
    print ('##########################################################')

import json
with open('TripAdvisor飯店評論.json', 'w') as f:                               #轉成.json檔
    json.dump(projectList, f)