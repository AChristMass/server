from django import views
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.views.generic import ListView

from ifc.models import IfcModel
from mission.forms import DeplacementMissionForm
from mission.models import DeplacementMissionModel


class DeplacementMissionView(views.View):

    def post(self, request):
        form = DeplacementMissionForm(request.POST)
        if form.is_valid():
            try:
                ifc = IfcModel.objects.get(pk=request.POST['ifc_id'])
                DeplacementMissionModel(
                    ifc=ifc,
                    floor=request.POST["floor"],
                    start_space=request.POST["start_space"],
                    end_space=request.POST["end_space"]).save()
                return HttpResponse(status=200, content="ok")
            except ObjectDoesNotExist:
                return HttpResponse(status=400, content="Ifc don't exist")
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
        except ObjectDoesNotExist:
            return HttpResponse(status=400, content="Mission don't exist")


class DeplacementMissionListView(ListView):
    model = DeplacementMissionModel

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return JsonResponse(list(queryset.values()), status=200, safe=False)
