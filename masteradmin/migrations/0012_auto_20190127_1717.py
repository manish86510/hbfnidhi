# Generated by Django 2.1.4 on 2019-01-27 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('masteradmin', '0011_auto_20190125_1618'),
    ]

    operations = [
        migrations.AddField(
            model_name='admin',
            name='description',
            field=models.CharField(max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='admin',
            name='facebook',
            field=models.CharField(max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='admin',
            name='linkedin',
            field=models.CharField(max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='admin',
            name='twitter',
            field=models.CharField(max_length=250, null=True),
        ),
    ]
