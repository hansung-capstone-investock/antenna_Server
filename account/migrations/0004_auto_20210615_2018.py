# Generated by Django 3.2 on 2021-06-15 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_alter_interestedstockdata_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interestedstockdata',
            name='company1',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='interestedstockdata',
            name='company10',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='interestedstockdata',
            name='company2',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='interestedstockdata',
            name='company3',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='interestedstockdata',
            name='company4',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='interestedstockdata',
            name='company5',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='interestedstockdata',
            name='company6',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='interestedstockdata',
            name='company7',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='interestedstockdata',
            name='company8',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='interestedstockdata',
            name='company9',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='interestedstockdata',
            name='group',
            field=models.CharField(default='', max_length=50),
        ),
    ]
