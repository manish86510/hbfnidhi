# Generated by Django 5.0.7 on 2024-09-24 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('masteradmin', '0015_alter_customer_mobile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='mobile',
            field=models.BigIntegerField(max_length=10, unique=True),
        ),
    ]