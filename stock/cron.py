from .models import *
from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
from django.utils import timezone
from pykrx import stock as st
from datetime import date
import pandas as pd
import time
from django.db.models import Q

def is_weekend():
    year = datetime.today().year
    month = datetime.today().month
    day = datetime.today().day
    d = date(year,month,day)
    return d.weekday() > 4

def getDailyMarketIndex():
    if is_weekend() is True:
        return
    url = "https://kr.investing.com/indices/south-korea-indices"
    html = BeautifulSoup(requests.get(url,
                                    headers={'User-agent': 'Mozilla/5.0'}).text, "lxml")
    field = [2, 5, 6, 7]
    # kospi , kosdaq, kospi200
    marketid = {'kospi':'pair_37426','kosdaq':'pair_38016','kospi200':'pair_37427'}

    for key, value in marketid.items():
        marketSoup = html.find('tr',{'id':f'{value}'})
        taglist=list()
        idx =0
        # 지수, 등락폭, 등락폭 퍼센트, 시간
        for tag in marketSoup:
            if idx in field:
                taglist.append(tag.text)
            idx+=1
        marketFK = MarketList.objects.using('stockDB').get(market = key)

        dtobj = datetime.strptime(taglist[3],'%H:%M:%S')
        dtobj = dtobj.replace(year=timezone.now().year,month=timezone.now().month,day=timezone.now().day)

        taglist[0] =float(taglist[0].replace(',',''))

        instance = dailyMarketIndex.objects.using('stockDB').create(
            market = marketFK,
            date = dtobj,
            changeNum = taglist[1],
            changePer = taglist[2],
            index = taglist[0],
            )
        instance.save(using='stockDB')

def clearDailyMarket():
    if is_weekend() is True:
        return
    dailyMarketIndex.objects.using('stockDB').all().delete()
    
def readMarket():
    if is_weekend() is True:
        return
    markets = {'Kospi':'1001','Kosdaq':'2001','Kospi200':'1028'} # 코스피, 코스닥, 코스피200
    today = datetime.today().strftime('%Y%m%d')
    
    for key in markets:
        df = st.get_index_ohlcv_by_date(today, today, f'{markets[key]}')
        df['날짜'] = df.index
        df = df.rename(columns={'날짜': 'date', '고가': 'high', '저가': 'low',
                                '종가': 'close',  '거래량': 'tradingVolume',
                                '거래대금': 'tradingPrice'})
        df = df.dropna()
        
        marketClass = str(key)
        instance = eval(marketClass)
        for r in df.itertuples():
            marketinfo = instance(
                date = r.date,
                high = r.high,
                low = r.low,
                close = r.close,
                tradingVolume = r.tradingVolume,
                tradingPrice = r.tradingPrice
            )
            marketinfo.save(using='stockDB')
            

def insertPrice():
    stocklist = StockList.objects.using('stockDB').all()
    
    codelist = list()
    for c in stocklist:
        codelist.append(c.code)
    today = datetime.today().strftime('%Y%m%d')
    for code in codelist:
        time.sleep(0.2)
        price_df = st.get_market_ohlcv_by_date("20210616", "20210617", f"{code}")
        stock_df = pd.DataFrame(index = price_df.index,columns=['date','open','high','low','close','volume'])    
        stock_df['date'] = stock_df.index
        stock_df['open'] = price_df['시가']
        stock_df['high'] = price_df['고가']
        stock_df['low'] = price_df['저가']
        stock_df['close'] = price_df['종가']
        stock_df['volume'] = price_df['거래량']
        strClass = 'StockX'+code
        try:
            instance = eval(strClass)
        except:
            continue
        
        for r in stock_df.itertuples():    
            d = r.date
            stockinfo = instance(
                date = d,
                open = r.open,
                high = r.high,
                low = r.low,
                close = r.close,
                volume =r.volume,
            )
            try:
                stockinfo.save(using='stockDB')
            except:
                continue
            

def insertPerPbr():
    stocklist = StockList.objects.using('stockDB').all()
    
    codelist = list()
    for c in stocklist:
        codelist.append(c.code)

    today = datetime.today().strftime('%Y%m%d')

    for code in codelist:
        time.sleep(0.2)

        per_df = st.get_market_fundamental_by_date(today, today, f"{code}")
        stock_df = pd.DataFrame(index = per_df.index,columns=['date','per','pbr'])    
        stock_df['date'] = stock_df.index
        
        try:
            stock_df['per'] = per_df['PER']
        except:
            pass
        try:
            stock_df['pbr'] = per_df['PBR']
        except:
            pass
        strClass = 'StockX'+code
        try:
            instance = eval(strClass)
        except:
            continue
        for r in stock_df.itertuples():    
            d = r.date
            try:
                stockF = instance.objects.using("stockDB").get(date =d)
            except:
                continue
            stockF.per = r.per
            stockF.pbr = r.pbr
            try:
                stockF.save(using='stockDB')
            except:
                continue


def insertCap():
    stocklist = StockList.objects.using('stockDB').all()
    
    codelist = list()
    
    for c in stocklist:
        codelist.append(c.code)
    today = (datetime.today()-timedelta(days=4)).strftime('%Y%m%d')
    for code in codelist:
        print(code)
        time.sleep(0.2)
        try:
            cap_df = st.get_market_cap_by_date(today, today, f"{code}")
        except:
            continue
        stock_df = pd.DataFrame(index = cap_df.index,columns=['date','cap'])    
        stock_df['date'] = stock_df.index

        try:
            stock_df['cap'] = cap_df['시가총액']
        except:
            continue
        strClass = 'StockX'+code
        try:
            instance = eval(strClass)
        except:
            continue
            
        for r in stock_df.itertuples():
            
            d = r.date
            
            try:
                stockF = instance.objects.using("stockDB").get(date =d)
            except:
                continue
            stockF.cap = r.cap
            try:
                stockF.save(using='stockDB')
            except:
                continue
            

def topHighStock():
    today = date.today() - timedelta(days=1)

    if today.weekday() == 5:
        today -= datetime.timedelta(days=1)
    elif today.weekday() ==6:
        today -= today-datetime.timedelta(days=2)
    
    if today.weekday() == 0:
        yesterday = today-timedelta(days=3)
    else:
        yesterday = today-timedelta(days=1)
    
    stocklist = StockList.objects.using('stockDB').all()
    
    gapdict = dict()
    codelist = dict()
    for c in stocklist:
        codelist[c.code] = c.company

    for key in codelist:
        strClass = 'StockX'+key
        try:
            instance = eval(strClass)
        except:
            continue
        
        try:
            todayInfo = instance.objects.using("stockDB").filter(
                Q(date=today) | Q(date=yesterday))
            gapPrice = todayInfo[0].close-todayInfo[1].close
            gapPercent = (gapPrice/todayInfo[0].close)
            gapdict[key] = round(gapPercent*100,2)
        except:
            continue
    
    gapdict = sorted(gapdict.items(), key=lambda x: x[1], reverse=True)
    print(gapdict)
    
    