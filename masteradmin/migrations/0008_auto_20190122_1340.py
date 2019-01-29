# Generated by Django 2.1.4 on 2019-01-22 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('masteradmin', '0007_auto_20190122_1247'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='husband_name',
            field=models.CharField(max_length=60, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='father_name',
            field=models.CharField(max_length=60, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='mother_name',
            field=models.CharField(max_length=60, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='post_office',
            field=models.CharField(max_length=30, null=True),
        ),
    ]