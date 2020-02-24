from django.urls import path

from ifc.views import IfcListView, IfcView


app_name = 'ifc'

urlpatterns = [
    path('single/<int:pk>/', IfcView.as_view(), name="single"),
    path('single/', IfcView.as_view(), name="create_ifc"),
    path('list/', IfcListView.as_view(), name="list")
]
