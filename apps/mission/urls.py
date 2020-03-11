from django.urls import path

from mission.views import (DeplacementMissionListView, DeplacementMissionView, StartMissionView,
                           MissionInProgListView)


app_name = 'mission'

urlpatterns = [
    path('api/', DeplacementMissionView.as_view(), name="main"),
    path('api/<int:pk>/', DeplacementMissionView.as_view(), name="main_pk"),
    path('api/list/', DeplacementMissionListView.as_view(), {'name': ''}, name="list"),
    path('api/<name>/list/', DeplacementMissionListView.as_view(), name="list"),
    path('api/start/', StartMissionView.as_view(), name="start"),
    path('api/list/inprog/', MissionInProgListView.as_view(), name="list")
]
