from django.db import models
from datetime import date

class Doctor(models.Model):
    name = models.CharField(max_length=100, verbose_name='اسم الطبيب')
    specialty = models.CharField(max_length=100, verbose_name='التخصص')
    max_sessions = models.IntegerField(default=10, verbose_name='الحد الأقصى للجلسات')
    preferred_clinics = models.JSONField(default=list, blank=True, verbose_name='تفضيلات العيادات')
    preferred_days = models.JSONField(default=list, blank=True, verbose_name='تفضيلات الأيام مع الشيفت')  # ✅ List مش Dict
    unavailable_days = models.JSONField(default=list, blank=True, verbose_name='الأيام غير المتاحة مع الشيفت')  # ✅ List
    shift_preference = models.JSONField(default=list, blank=True, verbose_name='تفضيلات المناوبة')
    has_training = models.BooleanField(default=False, verbose_name='مدرب')

    def __str__(self):
        return self.name


class Clinic(models.Model):
    name = models.CharField(max_length=100, verbose_name='اسم العيادة')
    days_available = models.JSONField(default=list, blank=True, verbose_name='أيام العمل')

    def __str__(self):
        return self.name

class Vacation(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, verbose_name='الطبيب')
    start_date = models.DateField(verbose_name='تاريخ بدء الإجازة')
    end_date = models.DateField(verbose_name='تاريخ نهاية الإجازة')

    def __str__(self):
        return f"{self.doctor.name} ({self.start_date} → {self.end_date})"

class Attendance(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, verbose_name='الطبيب')
    date = models.DateField(verbose_name='التاريخ')
    is_present = models.BooleanField(default=True, verbose_name='حاضر')

    def __str__(self):
        return f"{self.doctor.name} - {self.date} - {'✔' if self.is_present else '❌'}"

class ScheduleEntry(models.Model):
    DAY_CHOICES = [
        ('الأحد', 'الأحد'), ('الاثنين', 'الاثنين'), ('الثلاثاء', 'الثلاثاء'),
        ('الأربعاء', 'الأربعاء'), ('الخميس', 'الخميس'),
    ]

    SESSION_CHOICES = [
        (1, 'نهاري - الأولى'),
        (2, 'نهاري - الثانية'),
        (3, 'مسائي - الأولى'),
        (4, 'مسائي - الثانية'),
    ]

    day = models.CharField(max_length=20, choices=DAY_CHOICES, verbose_name='اليوم')
    session = models.IntegerField(choices=SESSION_CHOICES, verbose_name='الفترة')
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, verbose_name='العيادة')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='الطبيب')
    is_special = models.BooleanField(default=False, verbose_name='عيادة خاصة')
    is_coverage = models.BooleanField(default=False, verbose_name='تغطية')
    week_start_date = models.DateField(verbose_name='بداية الأسبوع', default=date.today)
    has_conflict = models.BooleanField(default=False, verbose_name='تعارض في الجدول')  # الحقل الجديد

    def __str__(self):
        return f"{self.day} - {self.get_session_display()} - {self.clinic.name}"

class LocationConfig(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, verbose_name='العيادة')
    is_active = models.BooleanField(default=True, verbose_name='مفعّل')
    period_1_enabled = models.BooleanField(default=True, verbose_name='نهاري - الأولى')
    period_2_enabled = models.BooleanField(default=True, verbose_name='نهاري - الثانية')
    period_3_enabled = models.BooleanField(default=True, verbose_name='مسائي - الأولى')
    period_4_enabled = models.BooleanField(default=True, verbose_name='مسائي - الثانية')

    def __str__(self):
        return (
            f"{self.clinic.name} (1:{'✅' if self.period_1_enabled else '❌'} | "
            f"2:{'✅' if self.period_2_enabled else '❌'} | "
            f"3:{'✅' if self.period_3_enabled else '❌'} | "
            f"4:{'✅' if self.period_4_enabled else '❌'})"
        )