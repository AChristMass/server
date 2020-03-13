from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.generic import ListView

from ifc.models import IfcModel
from mission import utils
from mission.forms import DeplacementMissionForm, SendMissionForm
from mission.graph import actions_and_path_from_ifc
from mission.models import DeplacementMissionModel, MissionInProgModel
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
                name = form.cleaned_data["name"]
                start_x = form.cleaned_data["start_x"]
                start_y = form.cleaned_data["start_y"]
                end_x = form.cleaned_data["end_x"]
                end_y = form.cleaned_data["end_y"]
                floor = form.cleaned_data["floor"]
                if not ifc.check_position(floor, [(start_x, start_y), (end_x, end_y)]):
                    print("INVALID POSITION")
                    return HttpResponse(status=400, content="invalid position")
                mission = DeplacementMissionModel.objects.create(
                    ifc=ifc, floor=floor, name=name,
                    start_x=start_x, start_y=start_y,
                    end_x=end_x, end_y=end_y)
                return JsonResponse(status=200, data=mission.to_dict())
            except IfcModel.DoesNotExist:
                return HttpResponse(status=404, content="Ifc does not exist")
        
        return HttpResponse(status=400, content=str(form.errors))
    
    
    def put(self, request, pk):
        form = DeplacementMissionForm(request.PUT)
        if form.is_valid():
            try:
                m = DeplacementMissionModel.objects.get(pk=pk)
                
                if form.cleaned_data['ifc_id'] != m.ifc.pk:
                    try:
                        m.ifc = IfcModel.objects.get(pk=form.cleaned_data['ifc_id'])
                    except IfcModel.DoesNotExist:
                        return HttpResponse(status=404, content="Ifc does not exist")
                m.name = form.cleaned_data["name"]
                m.floor = form.cleaned_data['floor']
                m.start_x = form.cleaned_data['start_x']
                m.start_y = form.cleaned_data['start_y']
                m.end_x = form.cleaned_data['end_x']
                m.end_y = form.cleaned_data['end_y']
                if not m.ifc.check_position(m.floor, [(m.start_x, m.start_y), (m.end_x, m.end_y)]):
                    return HttpResponse(status=400, content="invalid position")
                m.save()
                return JsonResponse(status=200, data=m.to_dict())
            except DeplacementMissionModel.DoesNotExist:
                return HttpResponse(status=404, content="Mission does not exist")
        return HttpResponse(status=400, content=str(form.errors))
    
    
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



class StartMissionView(View):
    
    def post(self, request):
        form = SendMissionForm(request.POST)
        if form.is_valid():
            try:
                mission = DeplacementMissionModel.objects.get(pk=form.cleaned_data["mission_id"])
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
            
            ifc_data = mission.ifc.get_data()
            
            base = robot_config["cell_div"]
            
            sx = utils.round_by_base(start[0], base, mini=ifc_data["x_min"])
            sy = utils.round_by_base(start[1], base, mini=ifc_data["y_min"])
            start = sx, sy
            
            ex = utils.round_by_base(end[0], base, mini=ifc_data["x_min"])
            ey = utils.round_by_base(end[1], base, mini=ifc_data["x_min"])
            end = ex, ey
            
            path, actions = actions_and_path_from_ifc(ifc_data, mission.floor, start, end,
                                                      robot_config)
            x, y = path.pop(0)
            data = {
                "robot":  {
                    "type":    "deplacement",
                    "actions": actions
                },
                "socket": {
                    "path": path
                }
            }
            
            layer = get_channel_layer()
            mission_inprog = MissionInProgModel.objects.create(mission=mission, robot=robot,
                                                               x=x, y=y)
            async_to_sync(layer.group_send)(str(robot.uuid),
                                            {
                                                "type":    "mission_start",
                                                "data":    data,
                                                "mission": mission_inprog
                                            })
            return JsonResponse(status=200, data=mission_inprog.to_dict())
        return HttpResponse(status=400, content=form.errors)



class MissionInProgListView(ListView):
    model = MissionInProgModel
    
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset().all()
        data = list()
        for mission_inprog in queryset:
            data.append(mission_inprog.to_dict())
        return JsonResponse(data, status=200, safe=False)
