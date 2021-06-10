from django.http.response import Http404
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from rest_framework.views import APIView
from datetime import datetime, timedelta
from .models import *
from scraping.models import *
import pandas as pd
import datetime as dt
import urllib.request as req
from urllib import parse
import requests
import json
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime, timedelta, tzinfo
from bs4 import BeautifulSoup
import requests
from threading import Timer
from pykrx import stock as st
from stock import stockScraping
from stock.serializers import *
from scraping.serializers import *
import pandas as pd
from django.db.models import Max, F
from stock import backtest
from stock import backtestdf
from stock import cmpM
import json
import time

def initApp(request):
    stockScraping.initSet()
    return HttpResponse("App initial table setting")

@api_view(['POST'])
def backtestapi(request):
    if request.method == 'POST':
        backT = backtest.Backtest(request.data)
        a = backT.backTesting()
        return HttpResponse(a)


@api_view(['GET'])
def kospiYearList(request):
    if request.method == 'GET':
        today = datetime.today()
        startdate = today + timedelta(days=-365)
        kospiList = Kospi.objects.using("stockDB").filter(date__range = [startdate, today])
        kospiList_serializer = KospiSerializer(kospiList,many = True)
        return Response(kospiList_serializer.data)

@api_view(['GET'])
def kosdaqYearList(request):
    if request.method == 'GET':
        today = datetime.today()
        startdate = today + timedelta(days=-365)
        kosdaqList = Kosdaq.objects.using("stockDB").filter(date__range = [startdate, today])
        kosdaqList_serializer = KosdaqSerializer(kosdaqList,many = True)
        return Response(kosdaqList_serializer.data)
    
@api_view(['GET'])
def kospi200YearList(request):
    if request.method == 'GET':
        today = datetime.today()
        startdate = today + timedelta(days=-365)
        kospi200List = Kospi200.objects.using("stockDB").filter(date__range = [startdate, today])
        kospi200List_serializer = Kospi200Serializer(kospi200List,many = True)
        return Response(kospi200List_serializer.data)



def insertPrice(request):
    stocklist_df = pd.read_csv("C:/Users/Junyong/Desktop/capstone_stockData/stocklist.csv",dtype=str)
    codelist = list()
    for c in stocklist_df.itertuples():
        codelist.append(c.code)
    
    for code in codelist:
        time.sleep(0.5)
        try:
            per_df = st.get_market_fundamental_by_date("20210608", "20210609", f"{code}")
        except:
            continue
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
                break
            stockF.per = r.per
            stockF.pbr = r.pbr
            
            try:
                stockF.save(using='stockDB')
            except:
                pass
            
    return HttpResponse("insert Done")

@api_view(['GET'])
def before3M(request):
    if request.method == 'GET':
        
        compareList=CompareMonth.objects.annotate(max_date=Max('date'))
        compareList1=compareList.values().filter(date__gte=F('max_date'))
        compare_serializer = CompareSerializer(compareList1, many=True)
        return Response(compare_serializer.data)

@api_view(['GET'])
def marketList(request):
    if request.method == 'GET':
        marketList = MarketList.objects.using("stockDB").all()
        marketList_serializer = MarketListSerializer(marketList,many = True)
        return Response(marketList_serializer.data)


@api_view(['POST'])
def stockSearchData(request):
    if request.method == 'POST':
        companyCode = request.data['companyCode']
        nowDate = (datetime.now()-timedelta(1)).strftime('%Y-%m-%d')
        exeStr = 'StockX{0}.objects.using("stockDB").filter(date__range=["2020-01-01", "{1}"])'.format(companyCode, nowDate)
        stockData = eval(exeStr)
        stockData_serializer = StockSerializer(stockData, many=True)

        stockName = StockList.objects.using("stockDB").filter(code = companyCode)
        stockName_serializer = StockListSerializer(stockName, many=True)
        companyName = stockName_serializer.data[0]['company']

        newsData = MainNews.objects.filter(summary__contains=companyName)
        news_serializer = MainNewsSerializer(newsData, many=True)

        res_dict = dict()
        
        res_dict['stockData'] = stockData_serializer.data
        res_dict['newsData'] = news_serializer.data
        
        res_json = json.dumps(res_dict, ensure_ascii=False)

        return HttpResponse(res_json)