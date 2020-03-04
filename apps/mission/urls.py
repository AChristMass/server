from django.urls import path

from mission.views import DeplacementMissionListView, DeplacementMissionView, SendMissionView


app_name = 'mission'

urlpatterns = [
    path('api/', DeplacementMissionView.as_view(), name="main"),
    path('api/<int:pk>/', DeplacementMissionView.as_view(), name="main_pk"),
    path('api/list/', DeplacementMissionListView.as_view(), name="list"),
    path('api/send/<int:pk>/', SendMissionView.as_view(), name="send")
]
