# Generated by Django 2.2.9 on 2020-09-06 02:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cops', '0021_cop_p'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cop',
            name='precinct',
        ),
    ]