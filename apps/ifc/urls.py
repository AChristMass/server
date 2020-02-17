from django.urls import path

from ifc.views import *

app_name = 'ifc'

urlpatterns = [
    path('single/', IfcView.as_view()),
    path('list/', IfcListView.as_view())
]
