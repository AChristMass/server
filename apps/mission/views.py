from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.generic import ListView

from ifc.models import IfcModel
from mission.forms import DeplacementMissionForm, SendMissionForm
from mission.models import DeplacementMissionModel
from robot.models import RobotModel



class DeplacementMissionView(View):
    
    def post(self, request):
        form = DeplacementMissionForm(request.POST)
        if form.is_valid():
            try:
                ifc = IfcModel.objects.get(pk=request.POST['ifc_id'])
                DeplacementMissionModel(
                    ifc=ifc,
                    floor=form.cleaned_data["floor"],
                    start_space=form.cleaned_data["start_space"],
                    end_space=form.cleaned_data["end_space"]).save()
                return HttpResponse(status=200, content="ok")
            except IfcModel.DoesNotExist:
                return HttpResponse(status=404, content="Ifc does not exist")
        return HttpResponse(status=400, content=str(form.errors))
    
    
    def put(self, request):
        mission_id = request.PUT['mission_id']
        try:
            mission = DeplacementMissionModel.objects.get(pk=mission_id)
            mission.floor = request.PUT['floor']
            mission.start_space = request.PUT['start_space']
            mission.end_space = request.PUT['end_space']
            mission.save()
            return HttpResponse(status=200, content="ok")
        except DeplacementMissionModel.DoesNotExist:
            return HttpResponse(status=404, content="Mission does not exist")



class DeplacementMissionListView(ListView):
    model = DeplacementMissionModel
    
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return JsonResponse(list(queryset.values()), status=200, safe=False)



class SendMissionView(View):
    
    def post(self, request, pk):
        form = SendMissionForm(request.POST)
        if form.is_valid():
            try:
                mission = DeplacementMissionModel.objects.get(pk=pk)
            except DeplacementMissionModel.DoesNotExist:
                return HttpResponse(status=404, content="Mission does not exist")
            try:
                robot = RobotModel.objects.get(pk=form.cleaned_data["robot_uuid"])
            except RobotModel.DoesNotExist:
                return HttpResponse(status=404, content="Robot does not exist")
            if not robot.connected:
                return HttpResponse(status=400, content="Robot is not connected")
            
            layer = get_channel_layer()
            
            async_to_sync(layer.group_send)(str(robot.uuid), {"type": "mission", "text_data": "test"})
            return HttpResponse(status=200, content="ok")
        return HttpResponse(status=400, content=form.errors)
