# Generated by Django 3.2.7 on 2021-10-19 01:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_customer_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='rootPrice',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
