from os import name
from textwrap import indent
from stock.serializers import StockSerializer
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import *
import pandas as pd
import datetime as dt
import urllib.request as req
from urllib import parse
from bs4 import BeautifulSoup
import requests
import json
from kiwipiepy import Kiwi, Option
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from account.serializers import *
from stock.serializers import *
import datetime
from datetime import timedelta
import pprint

# Create your views here.
@api_view(['GET', 'POST'])
def account_list(request):
    if request.method == 'GET':
        account = accountData.objects.all()
        account_serializer = AccountSerializer(account, many=True)
        return Response(account_serializer.data)

    elif request.method == 'POST':
        account_serializer = AccountSerializer(data=request.data)
        if account_serializer.is_valid():
            account_serializer.save()
            return Response(account_serializer.data, status=status.HTTP_201_CREATED)
        return Response(account_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    if request.method == 'POST':
        userid = request.data['id']
        userpw = request.data['password']

        account = accountData.objects.filter(id=userid, password=userpw)
        account_serializer = AccountSerializer(account, many=True)
        try:
            id = account_serializer.data[0]['id']
            password = account_serializer.data[0]['password']
        except IndexError:
            return JsonResponse({"code": "1001", "msg": "로그인 실패하셨습니다."}, status=200)
        if (id, password) == (userid, userpw):
            return JsonResponse({"code": "0000", "msg": "로그인 성공하셨습니다."}, status=200)

@api_view(['POST'])
def signup(request):
    if request.method == 'POST':
        account_serializer = AccountSerializer(data=request.data)
        if account_serializer.is_valid():
            account_serializer.save()
            interestedstockData(
                name = request.data['id']
            ).save()
            interestedstockData(
                name = request.data['id']
            ).save()
            interestedstockData(
                name = request.data['id']
            ).save()
            return JsonResponse({"code": "0000", "msg": "회원가입 성공하셨습니다."}, status=200)
        else:
            return JsonResponse({"code": "1001", "msg": "회원가입 실패하셨습니다."}, status=200)

@api_view(['POST'])
def interestedstock_Update(request):
    if request.method == 'POST':
        interestedstockData.objects.filter(id = request.data['id']).update(group=request.data['group'])
        interestedstockData.objects.filter(id = request.data['id']).update(company1 = request.data['company1'])
        interestedstockData.objects.filter(id = request.data['id']).update(company2 = request.data['company2'])
        interestedstockData.objects.filter(id = request.data['id']).update(company3 = request.data['company3'])
        interestedstockData.objects.filter(id = request.data['id']).update(company4 = request.data['company4'])
        interestedstockData.objects.filter(id = request.data['id']).update(company5 = request.data['company5'])
        interestedstockData.objects.filter(id = request.data['id']).update(company6 = request.data['company6'])
        interestedstockData.objects.filter(id = request.data['id']).update(company7 = request.data['company7'])
        interestedstockData.objects.filter(id = request.data['id']).update(company8 = request.data['company8'])
        interestedstockData.objects.filter(id = request.data['id']).update(company9 = request.data['company9'])
        interestedstockData.objects.filter(id = request.data['id']).update(company10 = request.data['company10'])

        interested = interestedstockData.objects.filter(id = request.data['id'])
        interested_serializer = InterestedstockSerializer(interested, many=True)
        dict_temp = {}

        for j in range(1,11):
            dict_temp['company{0}'.format(j)] = interested_serializer.data[0]['company{0}'.format(j)]
        interested_serializer.data[0]['companies'] = dict_temp
        for j in range(1,11):
            del interested_serializer.data[0]['company{0}'.format(j)]

        return JsonResponse(interested_serializer.data, safe=False)

@api_view(['POST'])
def interestedgroup_list(request):
    if request.method == 'POST':
        interested = interestedstockData.objects.filter(name = request.data['name'])
        interested_serializer = InterestedstockSerializer(interested, many=True)
        for i in range(0, 3):
            dict_temp = {}
            for j in range(1,11):
                dict_temp['company{0}'.format(j)] = interested_serializer.data[i]['company{0}'.format(j)]
            interested_serializer.data[i]['companies'] = dict_temp
        for i in range(0,3):
            for j in range(1,11):
                del interested_serializer.data[i]['company{0}'.format(j)]
        return JsonResponse(interested_serializer.data, safe=False)

@api_view(['POST'])
def interestedgroup_list_web(request):
    if request.method == 'POST':
        interested = interestedstockData.objects.filter(name = request.data['name'])
        interested_serializer = InterestedstockSerializer(interested, many=True)

        
        for i in range(0, 3):
            dict_temp = {}
            for j in range(1,11):
                company_name = interested_serializer.data[i]['company{0}'.format(j)]
                # dict_temp['company{0}'.format(j)]
                if (company_name == 'null') or (company_name is None) or (company_name == ""):
                    continue
                else:
                    print(i, company_name)
                    code = StockList.objects.using("stockDB").filter(company = company_name)
                    code_serializer = StockListSerializer(code, many=True)

                    company_code = code_serializer.data[0]['code']

                    today = (datetime.datetime.now()-timedelta(1)).strftime('%Y-%m-%d')
                    weeks_ago = (datetime.datetime.now()-timedelta(7)).strftime('%Y-%m-%d')

                    exeStr = 'StockX{0}.objects.using("stockDB").filter(date__range=["{1}", "{2}"])'.format(company_code, weeks_ago, today)
                    stockData = eval(exeStr)
                    stockData_serializer = StockSerializer(stockData, many=True)
                    stock_length = len(stockData_serializer.data) - 1

                    yesterday_close = stockData_serializer.data[stock_length-1]['close']
                    today_close = stockData_serializer.data[stock_length]['close']

                    # 전일비, 등락률
                    diff = today_close - yesterday_close
                    diffrate = diff / today_close * 100

                    dict_temp['company{0}'.format(j)] = {"company" : company_name, "code" : code_serializer.data[0]['code'],
                                                            "close" : today_close, "diff" : diff, "diffrate": round(diffrate,2)}

            interested_serializer.data[i]['companies'] = dict_temp
        for i in range(0,3):
            for j in range(1,11):
                del interested_serializer.data[i]['company{0}'.format(j)]

        return JsonResponse(interested_serializer.data, safe=False)
