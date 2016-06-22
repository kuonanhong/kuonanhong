# -*- coding: utf-8 -*-
import re

headers ={                                                                            #這是主頁面須載入之header,是DOC靜態文件,用get方法取得
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate, sdch, br',
'Accept-Language':'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4',
'Cache-Control':'max-age=0',
'Connection':'keep-alive',
'Cookie':'TAUnique=%1%enc%3AUl3cwI1xc%2FTwsb385vMtATZhvkrLn01BufRn5N1xwqg1zuHpUDBstg%3D%3D; __gads=ID=fd97053f079cb8ac:T=1464841916:S=ALNI_MbJojMYnpBrawgR9y_4NEBJNG0Deg; TAAuth2=%1%3%3A6417c520b203ebad2e7422a341efb8ec%3AAFrize7eFxrMHZAhEjQ1R6vp71NrngMb1kZQ3ZHBER7%2BN2hNipWsPSAotWXX1pbZ3xAHG1ZhXd0Q3UDH3TzzYTmGk2FYmBszCn%2BiADd8xOGwqaNYImrGQWkIEdU8I4igmlETEN8lGHVWt0YF2FusTjfhrgai7bTZV2SXUj07qHB1OY26BlgFXkCnN8%2FO9B4zK2V1tX3NP64xGnqBi0%2B%2FTghtDYYyI%2BF%2BFoXG863eckIm; TART=%1%enc%3A1uuQrU3JlwiuwCxmUqQISTwnGUaZsbIXPRFxT%2BYmI1nv5%2FKLFv4Gy6S2YdCGqRrgjcUVV%2FjQ5bY%3D; TASSK=enc%3AY%2B8faEoGrSzZeKuLBMQl4ux5o9FsuevcHHI2z1PzCTf%2BNEvcfA5zo4lPySHGFHQKS7ktjdRhPq0%3D; ServerPool=B; TATravelInfo=V2*AC.TPE*A.2*MG.-1*HP.2*FL.3*RVL.307399_161l305912_162l320581_163l310308_163l8557280_163l1628827_166l310298_168l579136_168l1811698_168l307253_168l294232_168l298156_169l298102_169l298143_169l298129_169*RS.1; CM=%1%HanaPersist%2C%2C-1%7Cpu_vr2%2C%2C-1%7Ct4b-pc%2C%2C-1%7CHanaSession%2C%2C-1%7CRCPers%2C%2C-1%7CWShadeSeen%2C%2C-1%7Cpu_vr1%2C%2C-1%7CFtrPers%2C%2C-1%7CHomeASess%2C1%2C-1%7CAWPUPers%2C%2C-1%7Ccatchsess%2C%2C-1%7Cbrandsess%2C%2C-1%7CCpmPopunder_1%2C17%2C1466235874%7CCCSess%2C%2C-1%7CCpmPopunder_2%2C8%2C-1%7Csesssticker%2C%2C-1%7C%24%2C%2C-1%7Ct4b-sc%2C%2C-1%7CMC_IB_UPSELL_IB_LOGOS2%2C%2C-1%7Cb2bmcpers%2C%2C-1%7CMC_IB_UPSELL_IB_LOGOS%2C%2C-1%7Csess_rev%2C%2C-1%7Csessamex%2C%2C-1%7Chac_ua_rd%2C%2C-1%7CSaveFtrPers%2C%2C-1%7Cpers_rev%2C%2C-1%7CMetaFtrSess%2C%2C-1%7CRBAPers%2C%2C-1%7CWAR_RESTAURANT_FOOTER_PERSISTANT%2C%2C-1%7CFtrSess%2C%2C-1%7CHomeAPers%2C%2C-1%7C+r_lf_1%2C%2C-1%7CRCSess%2C%2C-1%7C+r_lf_2%2C%2C-1%7Ccatchpers%2C3%2C1466498660%7CAWPUSess%2C%2C-1%7Cvr_npu2%2C%2C-1%7Csh%2C%2C-1%7CLastPopunderId%2C137-1859-null%2C-1%7Cpssamex%2C%2C-1%7C2016sticksess%2C%2C-1%7Cvr_npu1%2C%2C-1%7CCCPers%2C%2C-1%7CWAR_RESTAURANT_FOOTER_SESSION%2C%2C-1%7Cbrandpers%2C%2C-1%7Cb2bmcsess%2C%2C-1%7C2016stickpers%2C%2C-1%7CWarPopunder_Session%2C%2C-1%7CWarPopunder_Persist%2C%2C-1%7Cr_ta_2%2C%2C-1%7Cr_ta_1%2C%2C-1%7CSaveFtrSess%2C%2C-1%7CRBASess%2C%2C-1%7Cperssticker%2C%2C-1%7CMetaFtrPers%2C%2C-1%7C; TAReturnTo=%1%%2FHotels-g298102-Chubu-Hotels.html; roybatty=AOMDbZzmy90s9mKoPtWsNHqUKRdX2K6e8q2PTe8P95ou6Fa7lRaKCuElgDTy%2BqcGrgSFS0g9HeqR%2F%2FhqRrV4VY806mfTL4YwO92rJW9oEkTDsiTZ00wB2azLgCRLFpuCIcN94kkEsCPp5XY1T8x57l20Tvr8NKxZajMwoCdo61ve%2C1; _em_t=true; _em_vt=2785e35f3b615468d1d065d0383e574fb6bcd65735-250659555763adfe; _em_v=678fd4475a875b6cf84053b94fa35763997052fa42-008220205763adfe; TASession=%1%V2ID.C498087F11DF88475C752988CD9A3E62*SQ.105*MC.10568*LS.PageMoniker*GR.77*TCPAR.44*TBR.77*EXEX.69*ABTR.79*PPRP.93*PHTB.99*FS.33*CPU.14*HS.popularity*ES.popularity*AS.popularity*DS.5*SAS.popularity*FPS.oldFirst*TS.4704D895A3C3623D8925D3C0BAA24E20*FA.1*DF.0*LR.https%3A%2F%2Fwww%5C.google%5C.com%5C.tw%2F*LP.%2F*FBH.2*MS.-1*RMS.-1*TRA.true*LD.298102*BG.1021321*BT.hs248l; TAUD=LA-1466132863645-1*LG-17535886-2.1.F.*LD-17535888-.....; NPID=; EVT=gac.STANDARD_PAGINATION*gaa.next*gal.2*gav.0*gani.false*gass.Hotels*gasl.298102*gads.Hotels*gadl.298102*gapu.V2Ot%40woQK0AAAAWfxZUAAAAA*gams.1',
'Host':'www.tripadvisor.com.tw',
'Referer':'https://www.tripadvisor.com.tw/Hotels-g298102-Chubu-Hotels.html',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
}

headershotel ={                                                                       #這是經過翻頁動作新增post方法所用的header,是XHR文件,在執行翻頁時才會產生
'Accept':'text/javascript, text/html, application/xml, text/xml, */*',
'Accept-Encoding':'gzip, deflate, br',
'Accept-Language':'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4',
'Connection':'keep-alive',
'Content-Length':'175',
'Content-type':'application/x-www-form-urlencoded; charset=UTF-8',
'Cookie':'TAUnique=%1%enc%3AUl3cwI1xc%2FTwsb385vMtATZhvkrLn01BufRn5N1xwqg1zuHpUDBstg%3D%3D; __gads=ID=fd97053f079cb8ac:T=1464841916:S=ALNI_MbJojMYnpBrawgR9y_4NEBJNG0Deg; TAAuth2=%1%3%3A6417c520b203ebad2e7422a341efb8ec%3AAFrize7eFxrMHZAhEjQ1R6vp71NrngMb1kZQ3ZHBER7%2BN2hNipWsPSAotWXX1pbZ3xAHG1ZhXd0Q3UDH3TzzYTmGk2FYmBszCn%2BiADd8xOGwqaNYImrGQWkIEdU8I4igmlETEN8lGHVWt0YF2FusTjfhrgai7bTZV2SXUj07qHB1OY26BlgFXkCnN8%2FO9B4zK2V1tX3NP64xGnqBi0%2B%2FTghtDYYyI%2BF%2BFoXG863eckIm; TART=%1%enc%3A1uuQrU3JlwiuwCxmUqQISTwnGUaZsbIXPRFxT%2BYmI1nv5%2FKLFv4Gy6S2YdCGqRrgjcUVV%2FjQ5bY%3D; TASSK=enc%3AY%2B8faEoGrSzZeKuLBMQl4ux5o9FsuevcHHI2z1PzCTf%2BNEvcfA5zo4lPySHGFHQKS7ktjdRhPq0%3D; ServerPool=B; TATravelInfo=V2*AC.TPE*A.2*MG.-1*HP.2*FL.3*RVL.320581_163l310308_163l8557280_163l1628827_166l310298_168l579136_168l1811698_168l307253_168l294232_168l298156_169l298102_169l298143_169l298129_169l670212_169l1130965_169*RS.1; CM=%1%HanaPersist%2C%2C-1%7Cpu_vr2%2C%2C-1%7Ct4b-pc%2C%2C-1%7CHanaSession%2C%2C-1%7CRCPers%2C%2C-1%7CWShadeSeen%2C%2C-1%7Cpu_vr1%2C%2C-1%7CFtrPers%2C%2C-1%7CHomeASess%2C1%2C-1%7CAWPUPers%2C%2C-1%7Ccatchsess%2C%2C-1%7Cbrandsess%2C%2C-1%7CCpmPopunder_1%2C19%2C1466237941%7CCCSess%2C%2C-1%7CCpmPopunder_2%2C10%2C-1%7Csesssticker%2C%2C-1%7C%24%2C%2C-1%7Ct4b-sc%2C%2C-1%7CMC_IB_UPSELL_IB_LOGOS2%2C%2C-1%7Cb2bmcpers%2C%2C-1%7CMC_IB_UPSELL_IB_LOGOS%2C%2C-1%7Csess_rev%2C2%2C-1%7Csessamex%2C%2C-1%7Chac_ua_rd%2C%2C-1%7CSaveFtrPers%2C%2C-1%7Cpers_rev%2C%2C-1%7CMetaFtrSess%2C%2C-1%7CRBAPers%2C%2C-1%7CWAR_RESTAURANT_FOOTER_PERSISTANT%2C%2C-1%7CFtrSess%2C%2C-1%7CHomeAPers%2C%2C-1%7C+r_lf_1%2C%2C-1%7CRCSess%2C%2C-1%7C+r_lf_2%2C%2C-1%7Ccatchpers%2C3%2C1466498660%7CAWPUSess%2C%2C-1%7Cvr_npu2%2C%2C-1%7Csh%2C%2C-1%7CLastPopunderId%2C137-1859-null%2C-1%7Cpssamex%2C%2C-1%7C2016sticksess%2C%2C-1%7Cvr_npu1%2C%2C-1%7CCCPers%2C%2C-1%7CWAR_RESTAURANT_FOOTER_SESSION%2C%2C-1%7Cbrandpers%2C%2C-1%7Cb2bmcsess%2C%2C-1%7C2016stickpers%2C%2C-1%7CWarPopunder_Session%2C%2C-1%7CWarPopunder_Persist%2C%2C-1%7Cr_ta_2%2C%2C-1%7Cr_ta_1%2C%2C-1%7CSaveFtrSess%2C%2C-1%7CRBASess%2C%2C-1%7Cperssticker%2C%2C-1%7CMetaFtrPers%2C%2C-1%7C; TAReturnTo=%1%%2FHotels-g1120615-Hakuba_mura_Kitaazumi_gun_Nagano_Prefecture_Chubu-Hotels.html; roybatty=ANTVnhkM8iGx5AIWsq3Ie3L9OumK5zpk2YACVa1CwavJg%2F0TMzWykHV1CtRpURGf6XXl%2BpLddZ4f677lhLCPtOsaNQ4hHR7vGXOpGlfib7t%2Bdk9fT8JShbXwDk%2FVxy7ygd2eZwnUfsMNhmBRbxi5oEF%2FMHESwmALkfLNqTi9pZRY%2C1; _em_vt=bceae79e802c7172664065d0383e574fb6bcd65735-250659555763c643; _em_v=4898d3fc04dfababb4ccdf12657d5763c5cc6a09c9-546420195763c643; TASession=%1%V2ID.C498087F11DF88475C752988CD9A3E62*SQ.163*MC.10568*LS.PageMoniker*GR.77*TCPAR.44*TBR.77*EXEX.69*ABTR.79*PPRP.93*PHTB.99*FS.33*CPU.14*HS.popularity*ES.popularity*AS.popularity*DS.5*SAS.popularity*FPS.oldFirst*TS.4704D895A3C3623D8925D3C0BAA24E20*LF.zhTW*FA.1*DF.0*LR.https%3A%2F%2Fwww%5C.google%5C.com%5C.tw%2F*LP.%2F*FBH.2*MS.-1*RMS.-1*TRA.true*LD.1120615*BG.1120615*BT.hpey65; TAUD=LA-1466132863645-1*LG-23749540-2.1.F.*LD-23749542-.....; NPID=',
'Host':'www.tripadvisor.com.tw',
'Origin':'https://www.tripadvisor.com.tw',
#'Referer':'https://www.tripadvisor.com.tw/Hotels-g1120615-Hakuba_mura_Kitaazumi_gun_Nagano_Prefecture_Chubu-Hotels.html',
'Referer':'',
'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36',
'X-Puid':'V2PF-QoQIHAAAMc3AwEAAAAN',
'X-Requested-With':'XMLHttpRequest'
}
#經觀察每個Hotel頁面的Cookie好像都不同,由於不傷大雅,故將它註解掉
payload ={                                                #這是經過翻頁動作新增post方法所用的data,是XHR文件
'seen':'0',
'sequence':'1',
'geo':'1120615',
'adults':'2',
'rooms':'1',
'searchAll':'false',
'requestingServlet':'Hotels',
'refineForm':'true',
'hs':'',
'o':'',
'pageSize':'',
'rad':'0',
'dateBumped':'NONE',
'displayedSortOrder':'popularity'
}

projectList = []
urlform = 'https://www.tripadvisor.com.tw'         #下面url所共有的表頭網址,每個在urllist上的網址代表每個地區
urlHotels = 'https://www.tripadvisor.com.tw/Hotels'
urllist = [
           '/Hotels-g298102-Chubu-Hotels.html'
           ]
#Kanto:關東地區;Kinki:近畿地區;Tohoku:東北地區;Shikoku:四國;Hokkaido:北海道;
#Kyushu_Okinawa:九州沖繩地區;Chubu:中部地區;Chugoku:中國地方

tempDic = {'agency':'','area':''}  #創一個Dictionary
tempDic['agency'] = u'TripAdvisor飯店評論'                              #將旅社姓名塞入key是agency的tempDic
tempDic['area'] = u'中部地區'
date = 'date{}'
comment = 'comment{}'
hotel = 'hotel{}'                                                          #創造此projectList的目的是最後要將結果以appendix的方式加入此projectList
def geturl(url):                                          #這函式是要自動化取得urllist內每個網址
    import requests
    from bs4 import BeautifulSoup
    rs = requests.session()
    res =rs.get(url,headers = headers)
    res.encoding = 'utf-8'
    return BeautifulSoup(res.text,'html.parser')

def geturlpost(url):
    import requests
    from bs4 import BeautifulSoup
    rs = requests.session()                 #記錄Cookie,但好像是多餘的
    headershotel['Referer'] = urlform_url
    payload['geo'] = re.search('\d{6}',urlele.split('-')[1]).group(0)        #運用regular expression 將urllist內各地區的代碼geo塞入payload['geo']以取得該地區飯店評論
    res =rs.post(url,headers = headershotel, data= payload)
    res.encoding = 'utf-8'
    return BeautifulSoup(res.text,'html.parser')

def getReviews(ele):                                       #這函式是要取得"該頁面下"的"每一個飯店"的旅客評論
#    url_HotelReviews = ele.select('a')[0]['href']          #此"旅客評論"網頁資訊藏在TripAdvisor該飯店的'a'標籤下
    print souphotel.select('.property_title')[1].text
    print ('FfFFFFFFFFFFFFFFfffffffffffffffffffff')
    urlform_HotelReviews = urlform + ele
    print urlform_HotelReviews
    print ('!!!!!!!!!!!!!!!!!!!!!!!!!')
    soupReview = geturl(urlform_HotelReviews)              #利用函式geturl將個別飯店的"旅客評論"網址帶入,這是點選TripAdvisor該飯店所額外產生的網頁
    print soupReview.select('#HEADING')[0].text
    print len(soupReview.select('#HEADING'))
    print ('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    countRivews = 0
    reviewPageNumber = 1
    or1 = 'or{}'
    EachDayCommentDic = {}
    for reviews in soupReview.select('.innerBubble'):            #先直接進行第一頁的評論
        countRivews += 1
        if len(reviews.select('.entry')) > 0:
            EachDayCommentDic[date.format(countRivews)] = reviews.select('.ratingDate')[0].text + ':' + reviews.select('.entry')[0].select('p')[0].text
            print EachDayCommentDic[date.format(countRivews)]

#    url_HotelReviews =  url_HotelReviews.split('-')[0]+'-'+url_HotelReviews.split('-')[1]+'-'+url_HotelReviews.split('-')[2]+'-'+ or1.format(10)+ '-' +url_HotelReviews.split('-')[3]+ '-' +url_HotelReviews.split('-')[4]+ '-' +url_HotelReviews.split('-')[5]
    url_HotelReviews =  ele.split('-')[0]+'-'+ele.split('-')[1]+'-'+ele.split('-')[2]+'-'+ele.split('-')[3]+'-'+ or1.format(10)+ '-' +ele.split('-')[4]+ '-' +ele.split('-')[5]+'#REVIEWS'
#    print ele.split('-')[4]
#    print ele.split('-')[5]
    print url_HotelReviews
    print urlform + url_HotelReviews
    print ('^^^^^^^^^^^^^^^^^^^^^^^')
    if (len(soupReview.select('.pageNumbers')) > 0):
        while(reviewPageNumber < len(soupReview.select('.pageNumbers')[0].select('a'))):  #先收集出現頁面(第一頁)的評論資料, 因為"第一頁"的標籤是'span'而第二頁之後的標籤是'a'
            urlform_HotelReviews = urlform + url_HotelReviews
            print urlform_HotelReviews
            print ('&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
            soupReview = geturl(urlform_HotelReviews)              #利用函式geturl將個別飯店的"旅客評論"網址帶入,這是點選TripAdvisor該飯店所額外產生的網頁

            for reviews in soupReview.select('.innerBubble'):
                countRivews += 1

                if len(reviews.select('.entry')) > 0:               #怕產生error_message,所以先給條件
                    EachDayCommentDic[date.format(countRivews)] = reviews.select('.ratingDate')[0].text + ':' + reviews.select('.entry')[0].select('p')[0].text
                    print EachDayCommentDic[date.format(countRivews)]

            reviewPageNumber += 1
            cout = 10*reviewPageNumber                  #這一行是因為評論網頁網址的規則,每翻一頁加10
            url_HotelReviews =  url_HotelReviews.split('-')[0]+'-'+url_HotelReviews.split('-')[1]+'-'+url_HotelReviews.split('-')[2]+'-'+url_HotelReviews.split('-')[3]+'-'+ or1.format(cout)+ '-' +url_HotelReviews.split('-')[5]+ '-' +url_HotelReviews.split('-')[6]
            #上面那一行(比較難懂),是指定"新的"url_HotelReviews,可以看到在split[2]和split[4]中間塞入or1.format(cout)以製造新的網址給while下一行的url_HotelReviews使用
            #直到整個while迴圈跑完, 即or1.format(cout)隨cout不同產生不同的評論網頁(url)
#            reviewPageDic[data_page_number.format(reviewPageNumber)] = reviewDic     #將此地區這個特定餐廳第一頁資訊塞成reviewPageDic[data_page_number n]
#            for element in souphotel.select('#sponsoredCouponListing'):
#                RestantDic[element.select('a')[0]['href']] =   EachDayCommentDic

            print hotel.format(countRest)
            print ('!!!!!!!!!!!!!!!!!!!!!!!!')
            print len(souphotel.select('.property_title'))
#        RestantDic[souphotel.select('#sponsoredCouponListing')[0].select('a')[0]['href']] = EachDayCommentDic
        print len(souphotel.select('.property_title'))
        print ('SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS')
        RestantDic[souphotel.select('.property_title')[0].text] = EachDayCommentDic
        print len(souphotel.select('.property_title'))
        for element in souphotel.select('.property_title'):
            print element.text
        print RestantDic[souphotel.select('.property_title')[0].text]
        print ('HIHiHiHiHiHiHiHiAAAAAAAAAAAAAAAAAAAAAA')

def getRestant():
    souphotel = geturl(urlhotel)
    countRest = 0
#    m = re.search(u'([0-9,]+)',souphotel.select('.tab_count')[0].text)
    if (len(souphotel.select('#sponsoredCouponListing')) > 0):    #怕有些飯店無旅客評論而產生erro_message,故限定一定有旅客評論的才列出來
        while(countRest < int(m.group(1))/10):
#            soup2 = geturlpost(urlHotels)
            if (souphotel.select('#sponsoredCouponListing')[0].select('a')[0]['href'] in List):
                continue
            else:
                print u'這是'+ tempDic['area']+u'地區第'+ str(countRest+1)+u'家餐廳'
                countRest = countRest +1                                 #不重複的餐廳才會進入if的條件之中,也才會計次(countRest+1)
                getReviews(souphotel.select('#sponsoredCouponListing')[0].select('a')[0]['href'])
                soupReview = geturl(urlform+souphotel.select('#sponsoredCouponListing')[0].select('a')[0]['href'])
                List.append(soupReview.select('#HEADING')[0].text)
                print ('--------------------------------------------------------------------------')
List = []                                                   #這個List的目的是用來判斷動態產生的餐廳數有無重複,方法是當動態產生的XHR文件若重複出現於List清單之中,則下方if條件不計次
oa = 'oa{}'
num = 1
resnum = 'resnum{}'
for urlele in urllist:
    urlform_url = urlform + urlele
    soup =geturl(urlform_url)
#    print soup.select('.geo_name')[1].text
    print (tempDic['area'] + u'這地區總還可以再分成約420個小的行政區域')
    countRest = 0
#        while(countRest < int(''.join(m.group(1).split(',')))):      #循環列出這地區這些餐廳名稱與評論, 每個地區平均約有上千筆餐廳,並估計有上百萬筆全球來的評論
    RestantDic={}                                            #先造一個空餐廳的子Dic,這是因為怕下方的getData2()中如果每次都將值塞入tempDic['hotel'],後面值會蓋住前面的值
    reviewDic = {}
    tourDic = {}
    placecount = 1
    placenum = 'placenum{}'
    for ele in soup.select('.geo_name'):      #這是中部地區主頁的第一頁,共約14頁,一頁有20個分較小的行政區域
        print ele.text                    #ele代表中部地區中再細分較小的行政區域
#        tourDic[placenum.format(placecount)] = ele.text     #將這些較小的行政區域(如白馬村(101)先塞入tourDic字典之中(這代表白馬村這地區有101間餐廳)

        urlhotel =  urlform + ele.select('a')[0]['href']    #此網頁連結到(比方白馬村(101))白馬村之下101家餐廳之頁面
        print urlhotel
#        headers['Cookie'] = 'TAUnique=%1%enc%3AUl3cwI1xc%2FTwsb385vMtATZhvkrLn01BufRn5N1xwqg1zuHpUDBstg%3D%3D; __gads=ID=fd97053f079cb8ac:T=1464841916:S=ALNI_MbJojMYnpBrawgR9y_4NEBJNG0Deg; TAAuth2=%1%3%3A6417c520b203ebad2e7422a341efb8ec%3AAFrize7eFxrMHZAhEjQ1R6vp71NrngMb1kZQ3ZHBER7%2BN2hNipWsPSAotWXX1pbZ3xAHG1ZhXd0Q3UDH3TzzYTmGk2FYmBszCn%2BiADd8xOGwqaNYImrGQWkIEdU8I4igmlETEN8lGHVWt0YF2FusTjfhrgai7bTZV2SXUj07qHB1OY26BlgFXkCnN8%2FO9B4zK2V1tX3NP64xGnqBi0%2B%2FTghtDYYyI%2BF%2BFoXG863eckIm; TART=%1%enc%3A1uuQrU3JlwiuwCxmUqQISTwnGUaZsbIXPRFxT%2BYmI1nv5%2FKLFv4Gy6S2YdCGqRrgjcUVV%2FjQ5bY%3D; TASSK=enc%3AY%2B8faEoGrSzZeKuLBMQl4ux5o9FsuevcHHI2z1PzCTf%2BNEvcfA5zo4lPySHGFHQKS7ktjdRhPq0%3D; ServerPool=B; TATravelInfo=V2*AC.TPE*A.2*MG.-1*HP.2*FL.3*RVL.310308_163l8557280_163l1628827_166l310298_168l579136_168l1811698_168l307253_168l294232_168l298156_169l298102_169l298143_169l298129_169l670212_169l1130965_169l1127347_169*RS.1; CM=%1%HanaPersist%2C%2C-1%7Cpu_vr2%2C%2C-1%7Ct4b-pc%2C%2C-1%7CHanaSession%2C%2C-1%7CRCPers%2C%2C-1%7CWShadeSeen%2C%2C-1%7Cpu_vr1%2C%2C-1%7CFtrPers%2C%2C-1%7CHomeASess%2C1%2C-1%7CAWPUPers%2C%2C-1%7Ccatchsess%2C%2C-1%7Cbrandsess%2C%2C-1%7CCpmPopunder_1%2C20%2C1466255684%7CCCSess%2C%2C-1%7CCpmPopunder_2%2C11%2C-1%7Csesssticker%2C%2C-1%7C%24%2C%2C-1%7Ct4b-sc%2C%2C-1%7CMC_IB_UPSELL_IB_LOGOS2%2C%2C-1%7Cb2bmcpers%2C%2C-1%7CMC_IB_UPSELL_IB_LOGOS%2C%2C-1%7Csess_rev%2C3%2C-1%7Csessamex%2C%2C-1%7Chac_ua_rd%2C%2C-1%7CSaveFtrPers%2C%2C-1%7Cpers_rev%2C%2C-1%7CMetaFtrSess%2C%2C-1%7CRBAPers%2C%2C-1%7CWAR_RESTAURANT_FOOTER_PERSISTANT%2C%2C-1%7CFtrSess%2C%2C-1%7CHomeAPers%2C%2C-1%7C+r_lf_1%2C%2C-1%7CRCSess%2C%2C-1%7C+r_lf_2%2C%2C-1%7Ccatchpers%2C3%2C1466498660%7CAWPUSess%2C%2C-1%7Cvr_npu2%2C%2C-1%7Csh%2C%2C-1%7CLastPopunderId%2C137-1859-null%2C-1%7Cpssamex%2C%2C-1%7C2016sticksess%2C%2C-1%7Cvr_npu1%2C%2C-1%7CCCPers%2C%2C-1%7CWAR_RESTAURANT_FOOTER_SESSION%2C%2C-1%7Cbrandpers%2C%2C-1%7Cb2bmcsess%2C%2C-1%7C2016stickpers%2C%2C-1%7CWarPopunder_Session%2C%2C-1%7CWarPopunder_Persist%2C%2C-1%7Cr_ta_2%2C%2C-1%7Cr_ta_1%2C%2C-1%7CSaveFtrSess%2C%2C-1%7CRBASess%2C%2C-1%7Cperssticker%2C%2C-1%7CMetaFtrPers%2C%2C-1%7C; TAReturnTo=%1%%2FHotels-g1120615-Hakuba_mura_Kitaazumi_gun_Nagano_Prefecture_Chubu-Hotels.html; roybatty=AOBnoUWAwgdOq9D79o5HIiyvBvJgQt6yKbw3h%2Bcg88wvSAr9qJVT09wAxMDGlIlB%2F0qWiIvDDY%2BdjsnktatsLD%2BbvTbl%2FMBKj4qFo835NSVEaPwJpLAevdplHlSUdVLuP8qbfdUfqJJj7dWlH3WoWotwyPSs2rR%2Ft8iKeJ15JGxy%2C1; _em_t=true; _em_vt=5afeac68dd681db543b065d0383e574fb6bcd65735-250659555763f7c6; _em_v=89806a6f89dfa29985af5f6ba3505763f68e42ffa3-541911425763f7c6; TASession=%1%V2ID.C498087F11DF88475C752988CD9A3E62*SQ.179*MC.10568*LS.PageMoniker*GR.77*TCPAR.44*TBR.77*EXEX.69*ABTR.79*PPRP.93*PHTB.99*FS.33*CPU.14*HS.popularity*ES.popularity*AS.popularity*DS.5*SAS.popularity*FPS.oldFirst*TS.4704D895A3C3623D8925D3C0BAA24E20*LF.zhTW*FA.1*DF.0*LR.https%3A%2F%2Fwww%5C.google%5C.com%5C.tw%2F*LP.%2F*FBH.2*MS.-1*RMS.-1*TRA.true*LD.1120615*BG.1120615*BT.hpeyig; TAUD=LA-1466132863645-1*LG-36424852-2.1.F.*LD-36424854-.....; NPID='
        souphotel = geturl(urlhotel)
        m = re.search(u'([0-9,]+)',souphotel.select('.tab_count')[0].text)       #取出這個地區總共有幾家旅行社的數目,用正規表達法取出(比方關東地區有3601家飯店)
        print (tempDic['area'] + u'這'+ ele.text+ u'地區總共有'+ ''.join(m.group(1).split(',')) +u'家精選的旅行社,為妳精選其中幾家的評論')
        print ('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
        print len(souphotel.select('#sponsoredCouponListing'))
#        countRest = 0
#        while(countRest < int(''.join(m.group(1).split(',')))):      #循環列出這地區這些餐廳名稱與評論, 每個地區平均約有上千筆餐廳,並估計有上百萬筆全球來的評論
        headershotel['Referer'] =urlhotel
        soup2 = geturlpost(urlHotels)
        RestantDic={}                                            #先造一個空餐廳的子Dic,這是因為怕下方的getData2()中如果每次都將值塞入tempDic['hotel'],後面值會蓋住前面的值
        reviewDic = {}
#        tempDicPage = {}
        hotel_comment_pagenum = 'hotel_comment_pagenum{}'
#        while(countRest < int(''.join(m.group(1).split(',')))/10):      #在網路不斷線下, 預計抓其中10分之1的餐廳量(不重複)需1天(p.s.因為跳出餐廳之頁面是亂數跳出)
        getRestant()                                                     #這一行呼叫函式getRestant()去抓多頁的餐廳,但因為是動態一個一個亂數產生,須控制數量,否則會在一個地區一直抓抓無窮久,進不到下個地區

        placecount += 1
        tourDic[(ele.text.strip()).encode('utf-8')] = RestantDic

    print ('###############################################################################')
    urlele = urlele.split('-')[0]+'-'+ urlele.split('-')[1]+'-'+oa.format(20*num)+'-'+urlele.split('-')[2]+'-'+urlele.split('-')[3]+'#LOCATION_LIST'  #翻到中部地區下個分頁

    for num in range (1,13):                                                           #中部地區共有13個分頁
        urlform_url = urlform + urlele
        soup =geturl(urlform_url)
        print urlform_url
        souphotel = geturl(urlhotel)
#        m = re.search(u'([0-9,]+)',souphotel.select('.tab_count')[0].text)       #取出這個地區總共有幾家旅行社的數目,用正規表達法取出(比方關東地區有3601家飯店)
        print (tempDic['area'] + u'這'+ ele.text+ u'地區總共有'+ ''.join(m.group(1).split(',')) +u'家精選的旅行社,為妳精選其中幾家的評論')
        print ('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
        print len(souphotel.select('#sponsoredCouponListing'))
        countRest = 0
#        while(countRest < int(''.join(m.group(1).split(',')))):      #循環列出這地區這些餐廳名稱與評論, 每個地區平均約有上千筆餐廳,並估計有上百萬筆全球來的評論
        RestantDic={}                                            #先造一個空餐廳的子Dic,這是因為怕下方的getData2()中如果每次都將值塞入tempDic['hotel'],後面值會蓋住前面的值
        reviewDic = {}
        tourDic = {}
#        tempDicPage = {}

        for ele in soup.select('.geo_name'):      #這是中部地區主頁的第一頁,共約14頁,一頁有20個分較小的行政區域
            print ele.text                    #ele代表中部地區中再細分較小的行政區域
            tourDic[placenum.format(placecount)] = ele.text     #將這些較小的行政區域(如白馬村(101)先塞入tourDic字典之中(這代表白馬村這地區有101間餐廳)
            urlhotel =  urlform + ele.select('a')[0]['href']
            print urlhotel
    #        headers['Cookie'] = 'TAUnique=%1%enc%3AUl3cwI1xc%2FTwsb385vMtATZhvkrLn01BufRn5N1xwqg1zuHpUDBstg%3D%3D; __gads=ID=fd97053f079cb8ac:T=1464841916:S=ALNI_MbJojMYnpBrawgR9y_4NEBJNG0Deg; TAAuth2=%1%3%3A6417c520b203ebad2e7422a341efb8ec%3AAFrize7eFxrMHZAhEjQ1R6vp71NrngMb1kZQ3ZHBER7%2BN2hNipWsPSAotWXX1pbZ3xAHG1ZhXd0Q3UDH3TzzYTmGk2FYmBszCn%2BiADd8xOGwqaNYImrGQWkIEdU8I4igmlETEN8lGHVWt0YF2FusTjfhrgai7bTZV2SXUj07qHB1OY26BlgFXkCnN8%2FO9B4zK2V1tX3NP64xGnqBi0%2B%2FTghtDYYyI%2BF%2BFoXG863eckIm; TART=%1%enc%3A1uuQrU3JlwiuwCxmUqQISTwnGUaZsbIXPRFxT%2BYmI1nv5%2FKLFv4Gy6S2YdCGqRrgjcUVV%2FjQ5bY%3D; TASSK=enc%3AY%2B8faEoGrSzZeKuLBMQl4ux5o9FsuevcHHI2z1PzCTf%2BNEvcfA5zo4lPySHGFHQKS7ktjdRhPq0%3D; ServerPool=B; TATravelInfo=V2*AC.TPE*A.2*MG.-1*HP.2*FL.3*RVL.310308_163l8557280_163l1628827_166l310298_168l579136_168l1811698_168l307253_168l294232_168l298156_169l298102_169l298143_169l298129_169l670212_169l1130965_169l1127347_169*RS.1; CM=%1%HanaPersist%2C%2C-1%7Cpu_vr2%2C%2C-1%7Ct4b-pc%2C%2C-1%7CHanaSession%2C%2C-1%7CRCPers%2C%2C-1%7CWShadeSeen%2C%2C-1%7Cpu_vr1%2C%2C-1%7CFtrPers%2C%2C-1%7CHomeASess%2C1%2C-1%7CAWPUPers%2C%2C-1%7Ccatchsess%2C%2C-1%7Cbrandsess%2C%2C-1%7CCpmPopunder_1%2C20%2C1466255684%7CCCSess%2C%2C-1%7CCpmPopunder_2%2C11%2C-1%7Csesssticker%2C%2C-1%7C%24%2C%2C-1%7Ct4b-sc%2C%2C-1%7CMC_IB_UPSELL_IB_LOGOS2%2C%2C-1%7Cb2bmcpers%2C%2C-1%7CMC_IB_UPSELL_IB_LOGOS%2C%2C-1%7Csess_rev%2C3%2C-1%7Csessamex%2C%2C-1%7Chac_ua_rd%2C%2C-1%7CSaveFtrPers%2C%2C-1%7Cpers_rev%2C%2C-1%7CMetaFtrSess%2C%2C-1%7CRBAPers%2C%2C-1%7CWAR_RESTAURANT_FOOTER_PERSISTANT%2C%2C-1%7CFtrSess%2C%2C-1%7CHomeAPers%2C%2C-1%7C+r_lf_1%2C%2C-1%7CRCSess%2C%2C-1%7C+r_lf_2%2C%2C-1%7Ccatchpers%2C3%2C1466498660%7CAWPUSess%2C%2C-1%7Cvr_npu2%2C%2C-1%7Csh%2C%2C-1%7CLastPopunderId%2C137-1859-null%2C-1%7Cpssamex%2C%2C-1%7C2016sticksess%2C%2C-1%7Cvr_npu1%2C%2C-1%7CCCPers%2C%2C-1%7CWAR_RESTAURANT_FOOTER_SESSION%2C%2C-1%7Cbrandpers%2C%2C-1%7Cb2bmcsess%2C%2C-1%7C2016stickpers%2C%2C-1%7CWarPopunder_Session%2C%2C-1%7CWarPopunder_Persist%2C%2C-1%7Cr_ta_2%2C%2C-1%7Cr_ta_1%2C%2C-1%7CSaveFtrSess%2C%2C-1%7CRBASess%2C%2C-1%7Cperssticker%2C%2C-1%7CMetaFtrPers%2C%2C-1%7C; TAReturnTo=%1%%2FHotels-g1120615-Hakuba_mura_Kitaazumi_gun_Nagano_Prefecture_Chubu-Hotels.html; roybatty=AOBnoUWAwgdOq9D79o5HIiyvBvJgQt6yKbw3h%2Bcg88wvSAr9qJVT09wAxMDGlIlB%2F0qWiIvDDY%2BdjsnktatsLD%2BbvTbl%2FMBKj4qFo835NSVEaPwJpLAevdplHlSUdVLuP8qbfdUfqJJj7dWlH3WoWotwyPSs2rR%2Ft8iKeJ15JGxy%2C1; _em_t=true; _em_vt=5afeac68dd681db543b065d0383e574fb6bcd65735-250659555763f7c6; _em_v=89806a6f89dfa29985af5f6ba3505763f68e42ffa3-541911425763f7c6; TASession=%1%V2ID.C498087F11DF88475C752988CD9A3E62*SQ.179*MC.10568*LS.PageMoniker*GR.77*TCPAR.44*TBR.77*EXEX.69*ABTR.79*PPRP.93*PHTB.99*FS.33*CPU.14*HS.popularity*ES.popularity*AS.popularity*DS.5*SAS.popularity*FPS.oldFirst*TS.4704D895A3C3623D8925D3C0BAA24E20*LF.zhTW*FA.1*DF.0*LR.https%3A%2F%2Fwww%5C.google%5C.com%5C.tw%2F*LP.%2F*FBH.2*MS.-1*RMS.-1*TRA.true*LD.1120615*BG.1120615*BT.hpeyig; TAUD=LA-1466132863645-1*LG-36424852-2.1.F.*LD-36424854-.....; NPID='
            souphotel = geturl(urlhotel)
            m = re.search(u'([0-9,]+)',souphotel.select('.tab_count')[0].text)       #取出這個地區總共有幾家旅行社的數目,用正規表達法取出(比方關東地區有3601家飯店)
            print (tempDic['area'] + u'這'+ ele.text+ u'地區總共有'+ ''.join(m.group(1).split(',')) +u'家精選的旅行社,為妳精選其中幾家的評論')
            print ('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
            print len(souphotel.select('#sponsoredCouponListing'))
#            countRest = 0
    #        while(countRest < int(''.join(m.group(1).split(',')))):      #循環列出這地區這些餐廳名稱與評論, 每個地區平均約有上千筆餐廳,並估計有上百萬筆全球來的評論
            headershotel['Referer'] = urlhotel
            soup2 = geturlpost(urlHotels)
            RestantDic={}                                            #先造一個空餐廳的子Dic,這是因為怕下方的getData2()中如果每次都將值塞入tempDic['hotel'],後面值會蓋住前面的值
            reviewDic = {}
#            tempDicPage = {}
            hotel_comment_pagenum = 'hotel_comment_pagenum{}'
            getRestant()                                     #這一行呼叫函式getRestant()去抓多頁的餐廳,但因為是動態一個一個亂數產生,須控制數量,否則會在一個地區一直抓抓無窮久,進不到下個地區

            placecount += 1
            tourDic[(ele.text.strip()).encode('utf-8')] = RestantDic

        print ('###############################################################################')
    num += 1
    tempDic['日本中部地區飯店評論'] = tourDic
    projectList.append(tempDic)

for ele in projectList:
    for key in sorted(ele):
        print key,ele[key]
    print ('##########################################################')

import json
with open('TripAdvisor飯店評論中部地區精簡正式版.json', 'w') as f:                               #轉成.json檔
    json.dump(projectList, f)