# Register your models here.
from django.contrib import admin

from mission.models import DeplacementMissionModel



@admin.register(DeplacementMissionModel)
class DeplacementMissionModelAdmin(admin.ModelAdmin):
    list_display = ["ifc", "floor", "start_x", "start_y", "end_x", "end_y"]
