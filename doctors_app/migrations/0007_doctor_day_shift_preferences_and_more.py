# Generated by Django 5.2 on 2025-04-27 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctors_app', '0006_alter_locationconfig_period_1_enabled_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='day_shift_preferences',
            field=models.JSONField(blank=True, default=dict, verbose_name='تفضيلات اليوم مع الشيفت'),
        ),
        migrations.AlterField(
            model_name='doctor',
            name='shift_preference',
            field=models.JSONField(blank=True, default=list, verbose_name='تفضيلات المناوبة العامة'),
        ),
    ]
