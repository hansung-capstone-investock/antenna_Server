# Generated by Django 3.2 on 2021-05-23 05:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='interestedstockdata',
            old_name='company',
            new_name='company1',
        ),
        migrations.AddField(
            model_name='interestedstockdata',
            name='company10',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='interestedstockdata',
            name='company2',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='interestedstockdata',
            name='company3',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='interestedstockdata',
            name='company4',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='interestedstockdata',
            name='company5',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='interestedstockdata',
            name='company6',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='interestedstockdata',
            name='company7',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='interestedstockdata',
            name='company8',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='interestedstockdata',
            name='company9',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
