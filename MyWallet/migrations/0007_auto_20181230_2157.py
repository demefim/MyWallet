# Generated by Django 2.1.2 on 2018-12-30 21:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MyWallet', '0006_auto_20181230_2152'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recurringtransaction',
            name='interval',
            field=models.IntegerField(choices=[(0, 'Disabled'), (6, 'Daily'), (5, 'Weekly'), (1, 'Monthly'), (2, 'Quarterly'), (3, 'Biannually'), (4, 'Annually')]),
        ),
    ]
