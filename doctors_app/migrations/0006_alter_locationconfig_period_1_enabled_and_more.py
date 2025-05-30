# Generated by Django 5.2 on 2025-04-26 03:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctors_app', '0005_scheduleentry_has_conflict'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locationconfig',
            name='period_1_enabled',
            field=models.BooleanField(default=True, verbose_name='نهاري - الأولى'),
        ),
        migrations.AlterField(
            model_name='locationconfig',
            name='period_2_enabled',
            field=models.BooleanField(default=True, verbose_name='نهاري - الثانية'),
        ),
        migrations.AlterField(
            model_name='scheduleentry',
            name='session',
            field=models.IntegerField(choices=[(1, 'نهاري - الأولى'), (2, 'نهاري - الثانية'), (3, 'مسائي - الأولى'), (4, 'مسائي - الثانية')], verbose_name='الفترة'),
        ),
    ]
