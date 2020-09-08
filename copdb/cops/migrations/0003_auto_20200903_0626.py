# Generated by Django 2.2.9 on 2020-09-03 06:26

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('geolocation', '0001_initial'),
        ('cops', '0002_auto_20200901_0337'),
    ]

    operations = [
        migrations.CreateModel(
            name='CopDBComplaint',
            fields=[
                ('complaint_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='cops.Complaint')),
                ('description', models.CharField(max_length=256)),
                ('copdb_complainer', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cops.CopDBComplainer')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='geolocation.Coordinates')),
            ],
            bases=('cops.complaint',),
        ),
        migrations.RemoveField(
            model_name='ccrbcomplaint',
            name='year_recieved',
        ),
        migrations.AddField(
            model_name='ccrbcomplaint',
            name='date_recieved',
            field=models.DateTimeField(default=datetime.datetime(2020, 9, 3, 6, 25, 57, 524513, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='conclusion',
            name='date_concluded',
            field=models.DateTimeField(default=datetime.datetime(2020, 9, 3, 6, 26, 19, 322081, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cop',
            name='ethnicity',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='cop',
            name='police_department',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='cop',
            name='rank',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='cop',
            name='sex',
            field=models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('U', 'Unable to determine')], default='U', max_length=1),
        ),
        migrations.AlterField(
            model_name='ccrbcomplaint',
            name='complainant_details',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='ccrbcomplaint',
            name='conclusion',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cops.Conclusion'),
        ),
        migrations.AlterField(
            model_name='complainer',
            name='description',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='complainer',
            name='name',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='conclusion',
            name='discipline',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='conclusion',
            name='type',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='cop',
            name='age',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='cop',
            name='badge_number',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='cop',
            name='description',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='cop',
            name='first_name',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='cop',
            name='last_name',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='cop',
            name='precinct',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.CreateModel(
            name='CopDBEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('complaint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cops.CopDBComplaint')),
                ('promoters', models.ManyToManyField(related_name='events_promoted', to=settings.AUTH_USER_MODEL)),
                ('sharers', models.ManyToManyField(related_name='events_shared', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
