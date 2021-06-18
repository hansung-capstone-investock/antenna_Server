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
from scraping.serializers import *
from django.db.models import Count


# dcinside 주식갤러리 크롤링
def parse_dc(request):
    url = 'https://gall.dcinside.com/board/lists/?id=neostock'
    # &page=1
    # 전체 페이지 읽어오기
    df = pd.DataFrame()
    for page in range(1, int(500)+1):
        page_url = '{}&page={}'.format(url, page)
        response_page = requests.get(page_url, headers={'User-agent': 'Mozilla/5.0'}).text
        df = df.append(pd.read_html(response_page)[0])
    df = df.dropna()
    df = df.drop_duplicates()

    dcData.truncate()

    kiwi = Kiwi()
    kiwi.prepare()
    temp = {}
    data = {}
    wordCounts = {}
    res = {}
    i = 0
    for nouns in df['제목']:
        noun = kiwi.analyze(nouns)
        temp = noun
        # 명사만 저장
        try:
            if (temp[0][0][0][1] == "NNG") or (temp[0][0][0][1] == "NNP") or (temp[0][0][0][1] == "NNB") or (temp[0][0][0][1] == "NR") or (temp[0][0][0][1] == "NP"):
                    if len(temp[0][0][0][0]) != 1:  # 한글자 단어 제거
                        data = temp[0][0][0][0]
                        if data not in wordCounts:
                            wordCounts[data] = 0
                        wordCounts[data] += 1
                        res[data] = wordCounts[data]
        except IndexError:
            continue
    for i, j in zip(res.keys(), res.values()):
        dcData(title=i, count=j).save()
    return 0

#네이버 증권 주요 뉴스 스크래핑
def crawlerNews(request):
    MainNews.truncate()

    BASE_URL = 'https://finance.naver.com/'
    
    now = dt.datetime.now()
    nowDate = now.strftime('%Y-%m-%d')
    nowTime = now.strftime('%H:%M:%S').split(':')[0]
    # url = BASE_URL+"news/mainnews.nhn?date="+str(nowDate)
    baseurl = BASE_URL+"news/mainnews.nhn?date="
    for i in range(0, 100):
        url = baseurl + str((now - dt.timedelta(i)).strftime('%Y-%m-%d'))
        res = req.urlopen(url)
        soup = BeautifulSoup(res,"html.parser",from_encoding='euc-kr')
        articleList = soup.select("#contentarea_left > div.mainNewsList > ul > li > dl")

        # 기사를 매시각 정각마다 1시간씩 받아오도록 반복문 설정
        title_list=[]
        
        for article in articleList:
            articleTime = article.select_one(".articleSummary > .wdate").get_text()
            # articleHour = int(articleTime.split(' ')[1].split(':')[0]) 
            # if articleHour <  int(nowTime)-1:
            #     break
            title = article.select_one(".articleSubject > a").get_text()
            summaryList = article.select_one(".articleSummary").get_text().strip().split('..')[0]
            linkList = article.select_one(".articleSubject > a")
            links = url
            links += linkList.attrs['href']
            link = url[0:25] + links[59:]
            
            mainnews = MainNews(
                title = title,
                summary= summaryList,
                link = link,
                publishDay = nowDate
            )
            mainnews.save()

    return HttpResponse("메인뉴스 크롤링")

def liveNews(request):
    LiveNews.truncate()
    url = 'https://finance.naver.com/news/news_list.nhn?&page='# {페이지}&date={날짜}
    now = dt.datetime.now()

    for i in range(0, 50):
        for j in range(1, 50):
            page_url = url + str(j) + str((now - dt.timedelta(i)).strftime('%Y%m%d'))
            res = req.urlopen(page_url)
            soup = BeautifulSoup(res,"html.parser",from_encoding='euc-kr')
            
            # newsList top
            titleList = soup.select("#contentarea_left > ul > li.newsList.top > dl > .articleSubject > a")
            summaryList = soup.select("#contentarea_left > ul > li.newsList.top > dl > .articleSummary")
            linkList = soup.select("#contentarea_left > ul > li.newsList.top > dl > .articleSubject > a")
            dateList = soup.select("#contentarea_left > ul > li.newsList.top > dl > .articleSummary > .wdate")
            for title, summary, link, date in zip(titleList, summaryList, linkList, dateList):
                link = link.attrs['href']
                links = url[0:25] + link[0:55]
                title = title.text
                summary = summary.text.strip().split('..')[0]
                date = date.text
                LiveNews(
                    title = title,
                    summary = summary,
                    link = links,
                    publishDate = date
                ).save()

            # newsList bottom
            titleList = soup.select("#contentarea_left > ul > li:nth-of-type(2) > dl > .articleSubject > a")
            summaryList = soup.select("#contentarea_left > ul > li:nth-of-type(2) > dl > .articleSummary")
            linkList = soup.select("#contentarea_left > ul > li:nth-of-type(2) > dl > .articleSubject > a")
            dateList = soup.select("#contentarea_left > ul > li:nth-of-type(2) > dl > .articleSummary > .wdate")
            for title, summary, link, date in zip(titleList, summaryList, linkList, dateList):
                link = link.attrs['href']
                links = url[0:25] + link[0:55]
                title = title.text
                summary = summary.text.strip().split('..')[0]
                date = date.text
                LiveNews(
                    title = title,
                    summary = summary,
                    link = links,
                    publishDate = date
                ).save()

    return HttpResponse("실시간 뉴스 크롤링 성공")

@api_view(['GET'])
def mainnews_list(request):
    if request.method == 'GET':
        news = MainNews.objects.all().order_by('publishDay')
        news_serializer = MainNewsSerializer(news, many=True)
        return Response(news_serializer.data)

@api_view(['GET'])
def livenews_list(request):
    if request.method == 'GET':
        livenews = LiveNews.objects.all().order_by('-publishDate')
        livenews_serializer = LiveNewsSerializer(livenews, many=True)
        return Response(livenews_serializer.data)

@api_view(['GET'])
def dc_list(request):
    if request.method == 'GET':
        dc = dcData.objects.all().order_by('-count')
        dc_serializer = DcSerializer(dc, many=True)
        return Response(dc_serializer.data)
