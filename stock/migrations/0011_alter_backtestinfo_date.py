# Generated by Django 3.2 on 2021-06-18 00:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0010_backtestinfo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backtestinfo',
            name='date',
            field=models.DateTimeField(),
        ),
    ]