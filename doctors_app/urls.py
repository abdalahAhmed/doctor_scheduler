from django.urls import path
from . import views
from .views import (
    export_current_schedule_excel, 
    export_next_schedule_excel, 
    export_current_schedule_en,   # ✅ ضيف ده
    export_next_schedule_en       # ✅ وضيف ده كمان
)

urlpatterns = [
    # ✅ الأطباء
    path('doctors/', views.doctors_list, name='doctors_list'),
    path('doctors/add/', views.add_doctor, name='add_doctor'),
    path('doctors/<int:doctor_id>/edit/', views.edit_doctor, name='edit_doctor'),
    path('doctors/<int:doctor_id>/delete/', views.delete_doctor, name='delete_doctor'),

    # ✅ العيادات
    path('clinics/', views.clinics_list, name='clinics_list'),
    path('clinics/add/', views.add_clinic, name='add_clinic'),
    path('clinics/<int:clinic_id>/edit/', views.edit_clinic, name='edit_clinic'),
    path('clinics/<int:clinic_id>/delete/', views.delete_clinic, name='delete_clinic'),

    # ✅ الإجازات
    path('vacations/', views.vacations_list, name='vacations_list'),
    path('vacations/add/', views.add_vacation, name='add_vacation'),
    path('vacations/<int:vacation_id>/edit/', views.edit_vacation, name='edit_vacation'),
    path('vacations/<int:vacation_id>/delete/', views.delete_vacation, name='delete_vacation'),

    # ✅ الحضور والغياب
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/add/', views.add_attendance, name='add_attendance'),
    path('attendance/<int:attendance_id>/edit/', views.edit_attendance, name='edit_attendance'),
    path('attendance/<int:attendance_id>/delete/', views.delete_attendance, name='delete_attendance'),

    # ✅ الجداول
    path('schedule/current/', views.current_schedule, name='current_schedule'),
    path('schedule/next/', views.next_schedule, name='next_schedule'),
    path('generate-schedule/', views.generate_schedule_view, name='generate_schedule'),

    # 🆕 حفظ تعديلات الجدول
    path('save-schedule-changes/', views.save_schedule_changes, name='save_schedule_changes'),

    # ✅ الصفحة الرئيسية للوحة التحكم
    path('', views.dashboard_view, name='doctor_dashboard'),

    # ✅ تصدير الجداول كـ Excel (عربي)
    path('export/current/', export_current_schedule_excel, name='export_current_schedule'),
    path('export/next/', export_next_schedule_excel, name='export_next_schedule'),

    # ✅ تصدير الجداول كـ Excel (إنجليزي)
    path('export/current/en/', export_current_schedule_en, name='export_current_schedule_en'),
    path('export/next/en/', export_next_schedule_en, name='export_next_schedule_en'),

    # ✅ زرار نقل الأسبوع القادم إلى الحالي
    path('move-week/', views.move_week, name='move_week'),

    # ✅ زرار توليد الأسبوع القادم يدويًا
    path('generate-schedule-manual/', views.generate_schedule_manual, name='generate_schedule_manual'),

    # ✅ صفحة العيادات المفعّلة
    path('active-locations/', views.active_locations_view, name='active_locations'),
    path('active-locations/edit/', views.active_locations_editable, name='active_locations_editable'),

]
