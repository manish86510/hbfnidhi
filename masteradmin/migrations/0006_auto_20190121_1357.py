# Generated by Django 2.1.4 on 2019-01-21 08:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('masteradmin', '0005_auto_20190121_1331'),
    ]

    operations = [
        migrations.AddField(
            model_name='fd',
            name='is_active',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='rd',
            name='is_active',
            field=models.IntegerField(null=True),
        ),
    ]
