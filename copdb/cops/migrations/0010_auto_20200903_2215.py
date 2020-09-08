# Generated by Django 2.2.9 on 2020-09-03 22:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cops', '0009_auto_20200903_2207'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complaint',
            name='complainant_ethnicity',
            field=models.CharField(blank=True, choices=[('White', 'White'), ('Black', 'Black'), ('Hispanic', 'Hispanic'), ('American Indian', 'American Indian'), ('Other Race', 'Other'), ('Unknown', 'Unknown')], max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='cop',
            name='ethnicity',
            field=models.CharField(blank=True, choices=[('White', 'White'), ('Black', 'Black'), ('Hispanic', 'Hispanic'), ('American Indian', 'American Indian'), ('Other Race', 'Other'), ('Unknown', 'Unknown')], max_length=16, null=True),
        ),
    ]