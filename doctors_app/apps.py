from django.apps import AppConfig

class DoctorsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'doctors_app'  # ✅ لازم يكون نفس اسم الفولدر بتاع التطبيق
