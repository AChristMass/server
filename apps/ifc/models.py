import json

import ifcopenshell
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models

from ifc.utils import connection_map, doors_locations, spaces_infos, spaces_polygons_data



class IfcModel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    data = JSONField(null=False, default=dict)
    file_path = models.FilePathField(path=settings.IFC_FILES_DIR)
    last_upload = models.DateTimeField(auto_now_add=True)
    
    
    @classmethod
    def parse(cls, ifc_file):
        ifc = ifcopenshell.open(ifc_file)
        
        floors_spaces = [(r.RelatingObject, r.RelatedObjects) for r in
                         ifc.by_type('IfcRelAggregates') if
                         r.RelatingObject.is_a('IfcBuildingStorey')]
        rel_space_boundary = ifc.by_type('IfcRelSpaceBoundary')
        data = {}
        x_min = None
        x_max = None
        y_min = None
        y_max = None
        for (floor, spaces) in floors_spaces:
            spaces_polygons, xi, xa, yi, ya = spaces_polygons_data(spaces, rel_space_boundary)
            data[floor.Name] = {
                'spacesInfos':    spaces_infos(spaces),
                'connectionMap':  connection_map(spaces),
                'spacesPolygons': spaces_polygons,
                'doorsLocations': doors_locations(spaces, rel_space_boundary)
            }
            if x_min is None or xi < x_min:
                x_min = xi
            if x_max is None or xa > x_max:
                x_max = xa
            if y_min is None or yi < y_min:
                y_min = yi
            if y_max is None or ya > y_max:
                y_max = ya
        data["x_min"] = x_min
        data["x_max"] = x_max
        data["y_min"] = y_min
        data["y_max"] = y_max
        return json.dumps(data)
    
    
    @classmethod
    def validate_ifc_file(cls, file):
        #  TODO : something
        return True
    
    
    def to_dict(self):
        return dict(
            id=self.pk,
            name=self.name,
            data=self.data,
            filePath=self.file_path
        )
