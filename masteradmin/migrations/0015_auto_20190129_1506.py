# Generated by Django 2.1.4 on 2019-01-29 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('masteradmin', '0014_auto_20190129_0901'),
    ]

    operations = [
        migrations.AddField(
            model_name='credittransaction',
            name='remark',
            field=models.CharField(max_length=80, null=True),
        ),
        migrations.AddField(
            model_name='debittransaction',
            name='remark',
            field=models.CharField(max_length=80, null=True),
        ),
    ]
