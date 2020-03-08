from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.generic import ListView

from robot.forms import RobotForm
from robot.models import RobotModel



class RobotView(View):
    
    def get(self, request):
        form = RobotForm(request.GET)
        if form.is_valid():
            try:
                robot = RobotModel.objects.get(pk=form.cleaned_data["uuid"])
                return JsonResponse(data=robot.to_dict(), status=200)
            except RobotModel.DoesNotExist:
                return HttpResponse(content="Robot don't exist", status=404)
        return HttpResponse(status=400, content=str(form.errors))
    
    
    def delete(self, request):
        uuid = request.body.decode().split("\r")[3][1:]
        try:
            RobotModel.objects.get(pk=uuid).delete()
            return HttpResponse(content="ok", status=200)
        except RobotModel.DoesNotExist:
            return HttpResponse(content="Robot does not exist", status=404)



class RobotListView(ListView):
    model = RobotModel
    
    
    def get_queryset(self):
        return self.model.objects.filter(name__icontains=self.kwargs['name'])
    
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset().all()
        data = list()
        for robot in queryset:
            data.append(robot.to_dict())
        return JsonResponse(data, status=200, safe=False)
