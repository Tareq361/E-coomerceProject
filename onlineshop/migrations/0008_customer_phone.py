# Generated by Django 3.2.9 on 2021-12-02 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('onlineshop', '0007_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='phone',
            field=models.CharField(default=1763, max_length=20),
            preserve_default=False,
        ),
    ]