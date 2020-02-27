from django.urls import path

from mission.views import DeplacementMissionListView, DeplacementMissionView, SendMissionView


app_name = 'mission'

urlpatterns = [
    path('mission/', DeplacementMissionView.as_view(), name="upload"),
    path('mission/<int:pk>', DeplacementMissionView.as_view(), name="modify"),
    path('list/', DeplacementMissionListView.as_view(), name="list"),
    path('send/<int:pk>/', SendMissionView.as_view(), name="send")
]
