from django.http.response import Http404
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.views import APIView
from .models import *
from scraping.models import *
import pandas as pd
import urllib.request as req
from urllib import parse
import requests
import json
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import datetime
from datetime import timedelta
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
import json
import time
from rest_framework.renderers import JSONRenderer

def initApp(request):
    stockScraping.initSet()
    return HttpResponse("App initial table setting")

@api_view(['POST'])
def backtestapi(request):
    
    if request.method == 'POST':
        backT = backtest.Backtest1(request.data)
        if backT.backTesting() is None:
            return JsonResponse(backT.errormsg)
        else:
            if backT.isValidFlag ==False:
                return JsonResponse(backT.errormsg)
            # backT.saveBack()
            return JsonResponse(backT.gapDict)

@api_view(['POST'])
def backAppapi(request):
    condict = request.data
    conditions = list()
    conlist = ['per','pbr','psr','roe','roa']
    for con in conlist:
        if condict[con][0]==-9999:
            del condict[con]
            continue
        temp = {
            con:
            [
            condict[con][0],
            condict[con][1],
            condict[con][2]
            ]
        }
        conditions.append(temp)
        del condict[con]
    condict["conditions"] = conditions
    if request.method == 'POST':
        backT = backtest.Backtest1(request.data)
        if backT.backTesting() is None:
            return JsonResponse(backT.errormsg)
        else:
            if backT.isValidFlag ==False:
                return JsonResponse(backT.errormsg)
            # backT.saveBack()
            return JsonResponse(backT.gapDict)


@api_view(['GET'])
def kospiYearList(request):
    if request.method == 'GET':
        today = datetime.datetime.today()
        startdate = today + timedelta(days=-365)
        kospiList = Kospi.objects.using("stockDB").filter(date__range = [startdate, today])
        kospiList_serializer = KospiSerializer(kospiList,many = True)
        return Response(kospiList_serializer.data)

@api_view(['GET'])
def kosdaqYearList(request):
    if request.method == 'GET':
        today = datetime.datetime.today()
        startdate = today + timedelta(days=-365)
        kosdaqList = Kosdaq.objects.using("stockDB").filter(date__range = [startdate, today])
        kosdaqList_serializer = KosdaqSerializer(kosdaqList,many = True)
        return Response(kosdaqList_serializer.data)
    
@api_view(['GET'])
def kospi200YearList(request):
    if request.method == 'GET':
        today = datetime.datetime.today()
        startdate = today + timedelta(days=-365)
        kospi200List = Kospi200.objects.using("stockDB").filter(date__range = [startdate, today])
        kospi200List_serializer = Kospi200Serializer(kospi200List,many = True)
        return Response(kospi200List_serializer.data)

@api_view(['GET'])
def before3M(request):
    if request.method == 'GET':
        compareList=Compare3Month.objects.using("stockDB").annotate(max_date=Max('date'))
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
        nowDate = (datetime.datetime.now()-timedelta(1)).strftime('%Y-%m-%d')
        exeStr = 'StockX{0}.objects.using("stockDB").order_by("-date").filter(date__range=["2020-01-01", "{1}"])'.format(companyCode, nowDate)
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