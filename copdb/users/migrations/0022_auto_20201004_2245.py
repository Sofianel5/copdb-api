# Generated by Django 2.2.9 on 2020-10-05 02:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0021_auto_20201004_2232'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='device',
            name='user',
        ),
        migrations.RemoveConstraint(
            model_name='androiddevice',
            name='unique_androiddevice',
        ),
        migrations.RemoveField(
            model_name='androiddevice',
            name='device_ptr',
        ),
        migrations.RemoveField(
            model_name='iosdevice',
            name='device_ptr',
        ),
        migrations.AddField(
            model_name='androiddevice',
            name='id',
            field=models.AutoField(auto_created=True, default=1, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='androiddevice',
            name='last_used',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='androiddevice',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='android_devices', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='iosdevice',
            name='id',
            field=models.AutoField(auto_created=True, default=1, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='iosdevice',
            name='last_used',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='iosdevice',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='ios_devices', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Device',
        ),
    ]
