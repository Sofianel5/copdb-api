# Generated by Django 2.2.9 on 2020-09-04 06:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cops', '0014_auto_20200904_0619'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cop',
            name='police_department',
        ),
    ]