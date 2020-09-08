# Generated by Django 2.2.9 on 2020-09-04 06:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('geolocation', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CopDBCity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='City')),
                ('epicenter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='geolocation.Coordinates')),
            ],
        ),
    ]