from django.db import models


class stockList(models.Model):
    code = models.CharField(max_length=10,primary_key=True)
    company = models.CharField(max_length=50)
    last_update = models.DateTimeField()
    #category = models.IntegerField()


class stockInfo(models.Model):
    code = models.ForeignKey(stockList, related_name = "stockcode", on_delete=models.CASCADE)
    date = models.DateTimeField()
    open = models.FloatField()      #시가
    high =models.FloatField()       #고가
    low = models.FloatField()       #저가
    close = models.FloatField()     #종가
    diff = models.FloatField()      #전일비
    volume = models.FloatField()    #거래량


class marketList(models.Model):
    name = models.CharField(max_length=20)


class marketInfo(models.Model):
    name = models.ForeignKey(marketList, on_delete=models.CASCADE)
    date = models.DateTimeField()
    score = models.FloatField()
    tradingVolume = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    