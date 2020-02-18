from django.urls import path

from mission.views import DeplacementMissionListView, DeplacementMissionView


app_name = 'mission'

urlpatterns = [
    path('upload/', DeplacementMissionView.as_view()),
    path('list/', DeplacementMissionListView.as_view())
]
