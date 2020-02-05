import time

from django import views
from django.conf import settings
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.views.generic import ListView

from ifc.forms import IfcForm
from ifc.models import IfcModel


class IfcView(views.View):

    def post(self, request):
        form = IfcForm(request.POST, request.FILES)
        if form.is_valid():
            name = request.POST['name']
            if IfcModel.objects.exists(name=name):
                return HttpResponse(status=400, content="Name taken")
            ifc_file_content = request.FILES['ifc_file'].read()
            saved_filename = f'{name}{time.time()}.ifc'
            with open(f'{settings.IFC_FILES_DIR}{saved_filename}', 'wb+') as new_file:
                new_file.write(ifc_file_content)
            graph = IfcModel.parse(ifc_file_content)
            IfcModel(name=name, filePath=saved_filename, graph=graph).save()
            return HttpResponse(status=200, content="ok")
        return HttpResponse(status=400, content=str(form.errors))


class IfcListView(ListView):
    model = IfcModel

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = serializers.serialize("json", queryset)
        return JsonResponse(data, status=200, safe=False)
