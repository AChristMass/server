from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.generic import ListView

from ifc.models import IfcModel, PositionModel
from robot.forms import RobotForm
from robot.models import RobotModel



class RobotView(View):
    
    def get(self, request):
        try:
            robot = RobotModel.objects.get(pk=request.GET["id"])
            return JsonResponse(data=robot.to_dict(), status=200, safe=False)
        except RobotModel.DoesNotExist:
            return HttpResponse(content="Robot don't exist", status=400)
    
    
    def post(self, request):
        form = RobotForm(request.POST)
        if form.is_valid():
            try:
                ifc = IfcModel.objects.get(pk=form.cleaned_data["ifc_id"])
            except IfcModel.DoesNotExist:
                return HttpResponse(status=404, content="Ifc does not exist")
            robot_position = PositionModel.objects.create(ifc=ifc,
                                                          floor=form.cleaned_data["floor"],
                                                          x=form.cleaned_data["x"],
                                                          y=form.cleaned_data["y"])
            robot = RobotModel.objects.create(name=form.cleaned_data["name"],
                                              position=robot_position)
            return JsonResponse(status=200, data=robot.to_dict())
        return HttpResponse(status=400, content=form.errors)



class RobotListView(ListView):
    model = RobotModel
    
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset().all()
        data = list()
        for robot in queryset:
            data.append(robot.to_dict())
        return JsonResponse(data, status=200, safe=False)
