import json

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.generic import ListView

from ifc.models import IfcModel
from mission.forms import DeplacementMissionForm, SendMissionForm
from mission.graph import actions_from_ifc
from mission.models import DeplacementMissionModel
from robot.models import RobotModel



class DeplacementMissionView(View):
    
    def get(self, request, pk):
        try:
            mission = DeplacementMissionModel.objects.get(pk=pk)
            return JsonResponse(status=200, data=model_to_dict(mission))
        except DeplacementMissionModel.DoesNotExist:
            return HttpResponse(status=404, content="Mission does not exist")
    
    
    def post(self, request):
        form = DeplacementMissionForm(request.POST)
        if form.is_valid():
            try:
                ifc = IfcModel.objects.get(pk=request.POST['ifc_id'])
                start_x = form.cleaned_data["start_x"]
                start_y = form.cleaned_data["start_y"]
                end_x = form.cleaned_data["end_x"]
                end_y = form.cleaned_data["end_y"]
                floor = form.cleaned_data["floor"]
                if not ifc.check_position(floor, [(start_x, start_y), (end_x, end_y)]):
                    return HttpResponse(status=400, content="invalid position")
                mission = DeplacementMissionModel.objects.create(
                    ifc=ifc, floor=floor,
                    start_x=start_x, start_y=start_y,
                    end_x=end_x, end_y=end_y)
                return JsonResponse(status=200, data=mission.to_dict())
            except IfcModel.DoesNotExist:
                return HttpResponse(status=404, content="Ifc does not exist")
        return HttpResponse(status=400, content=str(form.errors))
    
    
    def put(self, request, pk):
        try:
            mission = DeplacementMissionModel.objects.get(pk=pk)
            floor = request.PUT['floor']
            ifc_data = mission.ifc.get_data()
            if floor not in ifc_data:
                return HttpResponse(status=404, content="floor does not exist")
            mission.floor = floor
            mission.save()
            return HttpResponse(status=200, content="ok")
        except DeplacementMissionModel.DoesNotExist:
            return HttpResponse(status=404, content="Mission does not exist")
    
    
    def delete(self, request, pk):
        try:
            mission = DeplacementMissionModel.objects.get(pk=pk)
            mission.delete()
            return HttpResponse(status=200, content="ok")
        except DeplacementMissionModel.DoesNotExist:
            return HttpResponse(status=404, content="Mission does not exist")



class DeplacementMissionListView(ListView):
    model = DeplacementMissionModel
    
    
    def get_queryset(self):
        return self.model.objects.filter(name__icontains=self.kwargs['name'])
    
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset().all()
        data = list()
        for deplacement_mission in queryset:
            data.append(deplacement_mission.to_dict())
        return JsonResponse(data, status=200, safe=False)



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
            
            robot_config = settings.ROBOT_CONFIGS[robot.type]
            start = (mission.start_x, mission.start_y)
            end = (mission.end_x, mission.end_y)
            
            # TODO modify start and end in function of robot_config (node not in path = error)
            
            actions = actions_from_ifc(mission.ifc.get_data(), mission.floor, start, end,
                                       robot_config)
            
            data = {
                "actions": actions
            }
            layer = get_channel_layer()
            async_to_sync(layer.group_send)(str(robot.uuid),
                                            {"type": "mission", "text_data": json.dumps(data)})
            return HttpResponse(status=200, content="ok")
        return HttpResponse(status=400, content=form.errors)
