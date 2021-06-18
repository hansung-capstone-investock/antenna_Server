import datetime
from .models import *
from django.db.models import Q
import operator

def b3m():
    today = datetime.date.today() - datetime.timedelta(days=1)
    
    if today.weekday() == 5 or today.weekday() == 6:
        return
    stocklist = StockList.objects.using('stockDB').filter(
        Q(market = 1) | Q(market =2)
    )
    ###
    codelist = dict()
    for c in stocklist:
        codelist[c.code] = c.company
        
    gapdict = dict()
    codelist = dict()

    for key in codelist:
        strClass = 'StockX'+key
        try:
            instance = eval(strClass)
        except:
            continue
        
        Query=instance.objects.using("stockDB").order_by('-date')
        todayQ = Query[0]
        today = Query[0].date
        before3mQ = Query[60]
        
        gapPrice = todayQ.close-before3mQ.close
        gapPercent = (gapPrice/before3mQ.close)
        gapdict[key] = round(gapPercent*100,2)
    
    gapdict = sorted(gapdict.items(), key=lambda x: x[1], reverse=True)

    idx=0
    keylist=list()
    vlist = list()
    
    for t in gapdict:
        if idx == 10:
            break
        keylist.append(t[0])
        vlist.append(t[1])
        idx+=1
    
    for i in range(len(keylist)):
        cpModel = Compare3Month.objects.using('stockDB').create(
            date = today,
            stockcode = keylist[i],
            company = codelist[keylist[i]],
            gap = vlist[i],
            rank  = i+1
        )
        cpModel.save(using='stockDB')
        i+=1