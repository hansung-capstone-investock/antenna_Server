# Generated by Django 3.1.7 on 2021-04-29 03:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraping', '0004_delete_accountdata'),
    ]

    operations = [
        migrations.CreateModel(
            name='accountData',
            fields=[
                ('id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('password', models.CharField(max_length=100)),
            ],
        ),
    ]