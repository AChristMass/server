from django.conf.urls import include
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ifc/', include('apps.ifc.urls', namespace='ifc')),
    path('mission/', include('apps.mission.urls', namespace='mission')),
    path('robot/', include('apps.robot.urls', namespace='robot')),
]
