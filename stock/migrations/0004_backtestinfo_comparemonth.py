# Generated by Django 3.2 on 2021-06-10 15:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_alter_interestedstockdata_group'),
        ('stock', '0003_auto_20210607_1558'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompareMonth',
            fields=[
                ('date', models.DateField(primary_key=True, serialize=False)),
                ('stockcode1', models.CharField(max_length=10)),
                ('gap1', models.FloatField()),
                ('stockcode2', models.CharField(max_length=10)),
                ('gap2', models.FloatField()),
                ('stockcode3', models.CharField(max_length=10)),
                ('gap3', models.FloatField()),
                ('stockcode4', models.CharField(max_length=10)),
                ('gap4', models.FloatField()),
                ('stockcode5', models.CharField(max_length=10)),
                ('gap5', models.FloatField()),
                ('stockcode6', models.CharField(max_length=10)),
                ('gap6', models.FloatField()),
                ('stockcode7', models.CharField(max_length=10)),
                ('gap7', models.FloatField()),
                ('stockcode8', models.CharField(max_length=10)),
                ('gap8', models.FloatField()),
                ('stockcode9', models.CharField(max_length=10)),
                ('gap9', models.FloatField()),
                ('stockcode10', models.CharField(max_length=10)),
                ('gap10', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='BackTestInfo',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField(blank=True)),
                ('serial', models.CharField(blank=True, max_length=30)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.accountdata')),
            ],
        ),
    ]
