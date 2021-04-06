from django.db import models

class dcData(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title
    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

class fmkorData(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title
    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

class companyData(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=6)

    def __str__(self):
        return self.name
    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)