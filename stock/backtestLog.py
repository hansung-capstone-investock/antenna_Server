from .models import *
import csv

def getBacklog(id):
    query1 = BackTestInfo.objects.using("stockDB").filter(user=id)
    print(type(query1))
    logDict = dict()
    idx=0
    for backtest in query1:
        logFile_name = backtest.filename
        read_list=[]
        with open(f'../backfile/{logFile_name}.csv', mode='r') as file:
            for line in file:
                read_list.append(line)
            logDict[f'{logFile_name}']=read_list
        
        idx+=1
        
    return logDict
    