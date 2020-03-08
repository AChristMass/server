from django.urls import path

from ifc.views import IfcListView, IfcView


app_name = 'ifc'

urlpatterns = [
    path('api/<int:pk>/', IfcView.as_view(), name="main_pk"),
    path('api/', IfcView.as_view(), name="main"),
    path('api/<name>/list/', IfcListView.as_view(), name="list")
]
