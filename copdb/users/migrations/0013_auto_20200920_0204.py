# Generated by Django 2.2.9 on 2020-09-20 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20200920_0152'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactemail',
            name='value',
            field=models.CharField(default='', max_length=512),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='contactphone',
            name='value',
            field=models.CharField(default='', max_length=512),
            preserve_default=False,
        ),
    ]