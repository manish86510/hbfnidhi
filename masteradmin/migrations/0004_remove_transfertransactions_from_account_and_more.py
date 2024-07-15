# Generated by Django 5.0.6 on 2024-07-15 03:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('masteradmin', '0003_alter_transfertransactions_from_account_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transfertransactions',
            name='from_account',
        ),
        migrations.RemoveField(
            model_name='transfertransactions',
            name='to_account',
        ),
        migrations.AddField(
            model_name='transfertransactions',
            name='from_account_no',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transfers_out', to='masteradmin.savingaccount'),
        ),
        migrations.AddField(
            model_name='transfertransactions',
            name='to_account_no',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transfers_in', to='masteradmin.savingaccount'),
        ),
    ]
