import json

import ifcopenshell
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models

from ifc.parsing import doors_polygons, spaces_infos, spaces_polygons_data


# This class represents an IFC file with its name, data (the actual building), the path of the IFC file

class IfcModel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    data = JSONField(null=False, default=dict)
    file_path = models.FilePathField(path=settings.IFC_FILES_DIR)
    last_upload = models.DateTimeField(auto_now_add=True)
    
    # Parse an IFC file into an instance of this class
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
        data["floors"] = {}
        for (floor, spaces) in floors_spaces:
            spaces_polygons, xi, xa, yi, ya = spaces_polygons_data(spaces, rel_space_boundary)
            data["floors"][floor.Name] = {
                'spacesInfos':    spaces_infos(spaces),
                'spacesPolygons': spaces_polygons,
                'doorsPolygons':  doors_polygons(spaces, rel_space_boundary)
            }
            if x_min is None or xi < x_min:
                x_min = xi
            if x_max is None or xa > x_max:
                x_max = xa
            if y_min is None or yi < y_min:
                y_min = yi
            if y_max is None or ya > y_max:
                y_max = ya
        data["dimensions"] = {
            "xMin": x_min,
            "xMax": x_max,
            "yMin": y_min,
            "yMax": y_max
        }
        return data
    
    
    @classmethod
    def validate_ifc_file(cls, file):
        #  TODO : something
        return True
    
    # Returns the different data of an IFC in a dictionary
    def to_dict(self):
        return dict(
            id=self.pk,
            name=self.name,
            data=json.dumps(self.data),
            last_upload=self.last_upload
        )
    
    # Returns the data field of the IFC
    def get_data(self):
        data = self.data
        if type(self.data) is not dict:
            data = json.loads(data)
        return data
    
    # Returns whether the floor or the points are in the limits of the IFC
    def check_position(self, floor, points):
        ifc_data = self.get_data()
        x_min = ifc_data["dimensions"]["xMin"]
        x_max = ifc_data["dimensions"]["xMax"]
        y_min = ifc_data["dimensions"]["yMin"]
        y_max = ifc_data["dimensions"]["yMax"]
        if floor not in ifc_data["floors"]:
            return False
        for x, y in points:
            if x < x_min or x > x_max:
                return False
            if y < y_min or y > y_max:
                return False
        return True
