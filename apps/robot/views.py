from django import views
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView

from robot.forms import *
from robot.models import *


class RobotView(views.View):
    def get(self, request):
        try:
            robot = RobotModel.objects.get(pk=request.GET["id"])
            return JsonResponse(data=robot.as_json(), status=200, safe=False)
        except ObjectDoesNotExist:
            return HttpResponse(content="Robot don't exist", status=400)

    def post(self, request):
        form = RobotForm(request.POST)
        if form.is_valid():
            ifc = IfcModel.objects.get(pk=form.cleaned_data["ifc_id"])
            robot_position = RobotPositionModel(ifc=ifc,
                                                floor=form.cleaned_data["floor"],
                                                x=form.cleaned_data["x"],
                                                y=form.cleaned_data["y"])
            robot_position.save()
            robot = RobotModel(name=form.cleaned_data["name"],
                               position=robot_position)
            robot.save()
            return JsonResponse(status=200, data=robot.as_json())
        return HttpResponse(status=400, content=form.errors)

class RobotListView(ListView):
    model = RobotModel

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset().all()
        data = list()
        for robot in queryset:
            data.append(robot.as_json())
        return JsonResponse(data, status=200, safe=False)
