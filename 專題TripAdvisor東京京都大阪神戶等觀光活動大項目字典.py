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
urllist = ['/Attractions-g298184-Activities-Tokyo_Tokyo_Prefecture_Kanto.html',                #東京都觀光網頁
           '/Attractions-g298564-Activities-Kyoto_Kyoto_Prefecture_Kinki.html',                #京都觀光網頁
           '/Attractions-g298566-Activities-Osaka_Osaka_Prefecture_Kinki.html',                #大阪觀光網頁
           '/Attractions-g298562-Activities-Kobe_Hyogo_Prefecture_Kinki.html'                  #神戶觀光網頁
           ]
placeDic ={}

#tempDic = {u'景點與地標':'',u'自然與公園':'',u'購物':'',u'博物館':'',u'演唱會和表演':'',u'遊覽':'',u'戶外活動':'',u'動物園與水族館':'',u'飲食':'',u'休閒與娛樂':'',u'水上樂園與遊樂場':'',u'旅客資源':'',u'課程活動及工作仿':'',u'交通':'',u'spa與養生':'',u'夜生活':'',u'搭船遊覽與水上活動':'',u'活動':'',u'賭場與博弈':''}  #創一個Dictionary
def geturl(url):                                          #這函式是要自動化取得urllist內每個網址
    import requests
    from bs4 import BeautifulSoup
    rs = requests.session()
    res =rs.get(url,headers = headers)
    res.encoding = 'utf-8'
    return BeautifulSoup(res.text,'html.parser')

num = 'num{}'
for urlele in urllist:
    urlform_url = urlform + urlele
    soup =geturl(urlform_url)
    print urlform_url
    tempDic ={}

    for ele in soup.select('.filter.filter_xor'):
        try:                                                                    #最後一個"賭場與博弈"倒是真的沒.filter_name這標籤
            try:                                                                #最後一個"賭場與博弈"倒是真的沒href這標籤
                print ele.select('a')[0]['href']
                print ('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
                urltour = urlform + ele.select('a')[0]['href']                  #得到每個地區(東京,京都,大阪,神戶等)下的子網頁(如:景觀,遊樂中心等)
                print urltour
                souptour = geturl(urltour)
                count = 1
                tourDic = {}
                for element in souptour.select('.filter_content'):                 #為了萃取出子網頁(如:景觀,遊樂中心等)下更細的項目
#                    print ele.select('.filter_name')[0].text
#                    tempDic[ele.select('.filter_name')[0].text]=element.select('.filter_name')[0].text    #將更細的項目當成value塞入較大的項目(當成key)
                    tourDic[num.format(count)] = element.select('.filter_name')[0].text    #將更細的項目當成value塞入較大的項目(當成key)
                    print tourDic[num.format(count)]
                    count +=1
                print ele.select('.filter_name')[0].text
                tempDic[ele.select('.filter_name')[0].text] = tourDic
            except KeyError:
                continue

        except IndexError:
            continue

    placeDic[urlele.split('-')[3].split('_')[0]] = tempDic

ABC = placeDic.copy()                                       #這一步藉由copy的動做新建一個物件,以防止相同key值其value植被覆蓋
projectList.append(ABC)
print('=========================================================')
for ele in projectList:
    for key in sorted(ele):
        print key,ele[key]
print ('#############################################################')

import json
from json import load
with open('TripAdvistor東京京都大阪神戶光觀活動.json', 'w') as f:                               #轉成.json檔
    json.dump(projectList, f)



