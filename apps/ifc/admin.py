# Register your models here.
from django.contrib import admin

from ifc.models import IfcModel



@admin.register(IfcModel)
class IfcModelAdmin(admin.ModelAdmin):
    list_display = ("name", "file_path")
