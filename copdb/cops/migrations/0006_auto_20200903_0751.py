# Generated by Django 2.2.9 on 2020-09-03 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cops', '0005_auto_20200903_0748'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complainer',
            name='age',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cop',
            name='age',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
