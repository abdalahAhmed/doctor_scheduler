from django.contrib import admin
from .models import Doctor, LocationConfig

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialty', 'max_sessions', 'has_training')
    search_fields = ('name', 'specialty')
    list_filter = ('specialty', 'has_training')

@admin.register(LocationConfig)
class LocationConfigAdmin(admin.ModelAdmin):
    list_display = (
        'clinic', 'is_active',
        'period_1_enabled', 'period_2_enabled',
        'period_3_enabled', 'period_4_enabled',
    )
    list_editable = (
        'is_active',
        'period_1_enabled', 'period_2_enabled',
        'period_3_enabled', 'period_4_enabled',
    )
