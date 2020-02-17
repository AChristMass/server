from django.urls import path

from mission.views import *

app_name = 'mission'

urlpatterns = [
    path('upload/', DeplacementMissionView.as_view()),
    path('list/', DeplacementMissionListView.as_view())
]
