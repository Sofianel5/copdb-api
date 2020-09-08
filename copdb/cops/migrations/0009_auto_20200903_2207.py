# Generated by Django 2.2.9 on 2020-09-03 22:07

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('cops', '0008_auto_20200903_2151'),
    ]

    operations = [
        migrations.AddField(
            model_name='complaint',
            name='date_concluded',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='complaint',
            name='finding',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='complaint',
            name='outcome',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.DeleteModel(
            name='CCRBComplaint',
        ),
        migrations.DeleteModel(
            name='Conclusion',
        ),
    ]