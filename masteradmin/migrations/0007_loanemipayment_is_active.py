# Generated by Django 5.0.7 on 2024-09-23 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('masteradmin', '0006_recurringdeposit_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='loanemipayment',
            name='is_active',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]