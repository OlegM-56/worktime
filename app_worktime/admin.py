from django.contrib import admin
from app_worktime.models import *
from django.contrib.auth.models import Permission

# Register your models here.

admin.site.register(DocType)
admin.site.register(DocKind)
admin.site.register(WorkContent)
admin.site.register(AccountWorkTime)
admin.site.register(ReportWorkTimeTempl)
admin.site.register(ZakazHistory)
admin.site.register(WorkTimeFact)
admin.site.register(Department)
admin.site.register(Employee)

""" ==================== Додавання доступу до керуванням дозволами в адмін-панелі ======================="""
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'content_type', 'codename')


admin.site.register(Permission, PermissionAdmin)
