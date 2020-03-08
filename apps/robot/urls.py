from django.urls import path

from robot.views import RobotView, RobotListView


app_name = 'robot'

urlpatterns = [
    path('api/', RobotView.as_view(), name="main"),
    path('api/list/', RobotListView.as_view(), {'name': ''}, name="list"),
    path('api/<name>/list/', RobotListView.as_view(), name="list")
]
