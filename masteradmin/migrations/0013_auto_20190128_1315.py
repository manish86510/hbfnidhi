# Generated by Django 2.1.4 on 2019-01-28 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('masteradmin', '0012_auto_20190127_1717'),
    ]

    operations = [
        migrations.AddField(
            model_name='credittransaction',
            name='status',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='debittransaction',
            name='status',
            field=models.IntegerField(null=True),
        ),
    ]