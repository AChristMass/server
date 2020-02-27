from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.generic import ListView

from robot.models import RobotModel



class RobotView(View):
    
    def get(self, request):
        try:
            robot = RobotModel.objects.get(pk=request.GET["id"])
            return JsonResponse(data=robot.to_dict(), status=200, safe=False)
        except RobotModel.DoesNotExist:
            return HttpResponse(content="Robot don't exist", status=400)



class RobotListView(ListView):
    model = RobotModel
    
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset().all()
        data = list()
        for robot in queryset:
            data.append(robot.to_dict())
        return JsonResponse(data, status=200, safe=False)
