# Generated by Django 2.2.9 on 2020-09-20 05:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_remove_device_device_id'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='clipboarddata',
            options={'verbose_name': 'Clipboard Data Instance', 'verbose_name_plural': 'Clipboard Data'},
        ),
        migrations.AlterModelOptions(
            name='contactaddress',
            options={'verbose_name': 'Contact Address', 'verbose_name_plural': 'Contact Addresses'},
        ),
        migrations.AlterModelOptions(
            name='iosdevice',
            options={'verbose_name': 'iOS Device', 'verbose_name_plural': 'iOS Devices'},
        ),
        migrations.AlterModelOptions(
            name='networkinfo',
            options={'verbose_name': 'Network Info Instance', 'verbose_name_plural': 'Network Info Instances'},
        ),
    ]
