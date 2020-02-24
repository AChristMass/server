import json
import os
import time

from django import views
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.generic import ListView

from ifc.forms import IfcForm, IfcModifyForm
from ifc.models import IfcModel



class IfcView(views.View):
    
    def get(self, request, pk):
        try:
            ifc = IfcModel.objects.get(pk=pk)
            return JsonResponse(data=ifc.to_dict(), status=200, safe=False)
        except IfcModel.DoesNotExist:
            return HttpResponse(content="Ifc does not exist", status=404)
    
    
    def post(self, request):
        form = IfcForm(request.POST, request.FILES)
        if form.is_valid():
            
            name = form.cleaned_data["name"]
            if IfcModel.objects.filter(name=name).exists():
                return HttpResponse(status=409, content="Name taken")
            
            ifc_file_content = form.cleaned_data['ifc_file'].read()
            saved_filepath = os.path.join(settings.IFC_FILES_DIR, f'{name}{time.time()}.ifc')
            with open(saved_filepath, 'wb+') as new_file:
                new_file.write(ifc_file_content)
            
            graph = IfcModel.parse(saved_filepath)
            
            IfcModel.objects.create(name=name, file_path=saved_filepath, graph=graph)
            return HttpResponse(status=200, content="ok")
        return HttpResponse(status=400, content=str(form.errors))
    
    
    def put(self, request):
        form = IfcModifyForm(request.PUT, request.FILES)
        if form.is_valid():
            try:
                ifc_model = IfcModel.objects.get(pk=request.PUT['id'])
                ifc_model.name = request.PUT['name']
                
                if form.cleaned_data["ifc_file"]:
                    ifc_file_content = request.FILES['ifc_file'].read()
                    with open(ifc_model.filePath, 'wb+') as ifc_file:
                        ifc_file.write(ifc_file_content)
                    
                    ifc_model.graph = IfcModel.parse(ifc_model.filePath)
                
                ifc_model.save()
                ifc_json = IfcModel.objects.filter(pk=ifc_model.pk).values().first()
                ifc_json["graph"] = json.loads(ifc_json["graph"])
                return JsonResponse(status=200, data=ifc_json)
            except IfcModel.DoesNotExist:
                return HttpResponse(status=400, content="Ifc does not exist")
        return HttpResponse(status=400, content=str(form.errors))



class IfcListView(ListView):
    model = IfcModel
    
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset().all()
        data = list()
        for ifc in queryset:
            data.append(ifc.to_dict())
        return JsonResponse(data, status=200, safe=False)
