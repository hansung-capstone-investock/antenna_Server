from datetime import datetime, timedelta, date
from django.http.response import HttpResponse
from pandas.core.frame import DataFrame
from .models import *
import pandas as pd
from django.db.models import Q
from stock.serializers import *
import json

class Backtest1:
    errormsg={'error':'조건에 맞는 주식이 없습니다.'}

    def __init__(self, backTestInfo):
        self.isValidFlag = False
        self.haveStock = dict()
        self.gapDict = dict()
        self.tester = backTestInfo['id']
        self.gapDict['total'] = 0
        self.companyNum = 10
        self.start = date(int(backTestInfo['start'].split('-')[0]),int(backTestInfo['start'].split('-')[1]),int(backTestInfo['start'].split('-')[2]))
        self.end = date(int(backTestInfo['end'].split('-')[0]),int(backTestInfo['end'].split('-')[1]),int(backTestInfo['end'].split('-')[2]))
        self.targetDate = self.start
        self.strTarget = self.targetDate.strftime("%Y-%m-%d")
        
        #['per','pbr']
        self.sorts = list()
        
        #{'per':min,max,'pbr':min,max}
        self.condition = dict()
        
        for i in backTestInfo['conditions']:
            for key,value in i.items():
                self.condition[key] = [float(value[0]),float(value[1])]
                self.sorts.insert(value[2],key)
        
        self.sellConditionHigh = float(backTestInfo['sellCondition'][1])
        self.sellConditionLow = float(backTestInfo['sellCondition'][0])
        
        self.marketList = backTestInfo['market']
        self.sectorList = backTestInfo['sector']
        addSector = [1005,1006,1007,1008,1009,1010,1011,1012,1013,1014,1015]
        if 1027 in self.sectorList:
            for s in addSector:
                if s in self.sectorList:
                    continue
                self.sectorList.append(s)
        
        self.datelist =list()
        self.targetList = StockList.objects.using("stockDB").filter(
            Q(market__in = self.marketList) &
            Q(sectorcode__in = self.sectorList))
    
    def saveBack(self):
        num = BackTestInfo.objects.using("stockDB").filter(user = self.tester)
        userTestNum = len(num)+1
        file_name = self.tester+"_"+str(userTestNum)
        con = dict()
        con['start'] = self.start
        con['end'] =self.end
        con['sorts'] = self.sorts
        con['condition'] = self.condition
        con['sellcondition'] = [self.sellConditionHigh,self.sellConditionLow]
        con['marketList'] = self.marketList
        con['sectorList'] = self.sectorList
        dictData = {**con,**self.gapDict}
        # json_val = json.dumps(dictData)
        with open(f'../backfile/{file_name}.csv','w') as f:
            json.dump(dictData,f)
        
        # with open(f'../backfile/{file_name}.csv','w',newline="") as f:
        #     writer = csv.writer(f)
        #     for key, value in dictData.items():
        #         writer.writerow([key,value])
        
        backlog = BackTestInfo.objects.using("stockDB").create(
            user = self.tester,
            date = date.today(),
            filename = file_name
        )
        backlog.save()
        return

    def is_weekend(self,d):
        isWeek = date(d.year,d.month,d.day)
        return isWeek.weekday() > 4
    
    def getData(self):
        self.close_df = pd.DataFrame(index = self.datelist)
        self.per_df = pd.DataFrame( index = self.datelist)
        self.pbr_df = pd.DataFrame( index = self.datelist)
        self.psr_df = pd.DataFrame( index = self.datelist)
        self.roe_df = pd.DataFrame( index = self.datelist)
        self.roa_df = pd.DataFrame( index = self.datelist)
        
        idx =0
        for ticker in self.targetList:
            strClass = 'StockX'+ticker.code
            try:
                instance = eval(strClass)
            except:
                continue
            stockInfo = instance.objects.using("stockDB").filter(
                date__range=[self.start, self.end]
            )

            close_list = list()
            date_list = list()
            per_list=list()
            pbr_list=list()
            psr_list=list()
            roe_list=list()
            roa_list=list()
            
            for dayStock in stockInfo:
                date_list.append(dayStock.date)
                close_list.append(dayStock.close)
                per_list.append(dayStock.per)
                pbr_list.append(dayStock.pbr)
                psr_list.append(dayStock.psr)
                roe_list.append(dayStock.roe)
                roa_list.append(dayStock.roa) 
                
            try:
                self.close_df[f'{ticker.code}'] = close_list
            except:
                pass
            try:
                self.per_df[f'{ticker.code}'] = per_list
            except:
                pass
            try:
                self.pbr_df[f'{ticker.code}'] = pbr_list
            except:
                pass
            try:
                self.psr_df[f'{ticker.code}'] = psr_list
            except:
                pass
            try:
                self.roe_df[f'{ticker.code}'] = roe_list
            except:
                pass
            try:
                self.roa_df[f'{ticker.code}'] = roa_list
            except:
                pass
    
    def buyingStock(self,buyStockNum):
        idx =0
        buyflag=0

        #sorting
        df = pd.DataFrame()
        df['close'] = self.close_df.loc[self.targetDate]
        df['per'] = self.per_df.loc[self.targetDate]
        df['pbr'] = self.pbr_df.loc[self.targetDate]
        df['psr'] = self.psr_df.loc[self.targetDate]
        df['roe'] = self.roe_df.loc[self.targetDate]
        df['roa'] = self.roa_df.loc[self.targetDate]

        for con in self.sorts:
            con1 = df[con]> self.condition[con][0]
            con2 = df[con]< self.condition[con][1]
            df =df[con1&con2]
            
        sort_daily_df = df.sort_values(by=self.sorts,ascending=True)
        sort_daily_df['ticker']=sort_daily_df.index
        sort_daily_df.reset_index(drop=True,inplace=True)
        length = sort_daily_df.shape[0]
        
        while buyflag < buyStockNum:
            if length<=idx:
                break
            if sort_daily_df.loc[idx]['ticker'] in self.haveStock:
                idx+=1
                continue
            new_data = {
                'ticker' : sort_daily_df.loc[idx]['ticker'],
                'buy_date' : self.targetDate,
                'buy_price' : sort_daily_df.loc[idx]['close']
            }
            
            self.haveStock[new_data["ticker"]] = [self.targetDate, new_data['buy_price']]
            buyflag +=1
            self.isValidFlag =True
        
    def sellingStock(self):
        
        if not self.haveStock:
            return 10
        
        sellingNum =0
        delStock= list()
        
        for key,value in self.haveStock.items():
            todayPrice = self.close_df.loc[self.targetDate][key]
            boughtPrice = value[1]
            gap = todayPrice - boughtPrice
            gapPercent = gap/boughtPrice*100
            
            if self.sellConditionLow < gapPercent <self.sellConditionHigh:
                continue
            
            # 백테스팅 거래한 주식 정보 저장
            # sellInfo = {
            #     'ticker':key,
            #     'buy_date':value[0],
            #     'buy_price':value[1],
            #     'sell_date':self.targetDate,
            #     'sell_price':todayPrice,
            #     'profit':gapPercent
            # }
            # self.backTestLog_df = self.backTestLog_df.append(sellInfo,ignore_index=True)
            
            delStock.append(key)
            sellingNum +=1
            self.gapDict[self.strTarget]+=gapPercent
            
        for l in delStock:
            del self.haveStock[l]
        return sellingNum
    
    # 마지막날 모든 주식 판매
    def sellingStockAll(self):
        self.strTarget = self.targetDate.strftime("%Y-%m-%d")
        for key,value in self.haveStock.items():
            todayPrice = self.close_df.loc[self.targetDate][key]
            boughtPrice = value[1]
            gap = todayPrice - boughtPrice
            gapPercent = gap/boughtPrice*100
            
            # sellInfo = {
            #     'ticker':key,
            #     'buy_date':value[0],
            #     'buy_price':value[1],
            #     'sell_date':self.targetDate,
            #     'sell_price':todayPrice,
            #     'profit':gapPercent
            # }
            # self.backTestLog_df = self.backTestLog_df.append(sellInfo,ignore_index=True)
            
            self.gapDict[self.strTarget]=gapPercent
    
    #일일 테스팅
    def dailyTesting(self):
        
        buyStockNum = 10
        self.gapDict[self.strTarget] =0
        
        if self.targetDate !=self.start:
            buyStockNum = self.sellingStock()
        
        if buyStockNum == 0:
            return

        #조건에 맞는 주식 구매
        self.buyingStock(buyStockNum)
        return True
        
    def backTesting(self):
        if len(self.targetList) == 0:
            return 
        stockInfo = StockX000020.objects.using("stockDB").filter(
                date__range=[self.start, self.end]
            )
        for st in stockInfo:
            self.datelist.append(st.date)
            
        while True:
            if self.start not in self.datelist:
                self.start += timedelta(days=1)
                continue
            self.targetDate = self.start
            break
        self.getData()
        
        while self.targetDate != self.end:
            if self.targetDate not in self.datelist:
                self.targetDate += timedelta(days=1)
                continue

            self.strTarget = self.targetDate.strftime("%Y-%m-%d")
            
            if self.is_weekend(self.targetDate) == True:
                self.targetDate += timedelta(days=1)
                continue
                        
            if self.dailyTesting() == False:
                self.targetDate += timedelta(days=1)
                continue
            
            self.gapDict['total']+=self.gapDict[self.strTarget]
            self.targetDate += timedelta(days=1)

        while self.targetDate not in self.datelist:
            self.targetDate -= timedelta(days=1)

        self.sellingStockAll()
        self.gapDict['total']+=self.gapDict[self.strTarget]
        # self.backTestLog_df.to_csv("backtestLog.csv")
        temp = self.gapDict['total']
        del self.gapDict['total']
        self.gapDict['total'] = temp
        return 100
    