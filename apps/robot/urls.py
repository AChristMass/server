from django.urls import path

from robot.views import RobotView, RobotListView

app_name = 'robot'

urlpatterns = [
    path('', RobotView.as_view()),
    path('list/', RobotListView.as_view())
]
