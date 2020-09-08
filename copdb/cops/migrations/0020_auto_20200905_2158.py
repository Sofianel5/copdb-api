# Generated by Django 2.2.9 on 2020-09-06 01:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cops', '0019_auto_20200905_2144'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='precinct',
            constraint=models.UniqueConstraint(fields=('name', 'police_department'), name='unique_precinct'),
        ),
    ]