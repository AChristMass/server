import json

import ifcopenshell
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models

from ifc.utils import connection_map, doors_locations, spaces_infos, spaces_polygons



class IfcModel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    graph = JSONField(null=False, default=dict)
    filePath = models.FilePathField(path=settings.IFC_FILES_DIR)
    
    
    @classmethod
    def parse(cls, ifc_file):
        ifc = ifcopenshell.open(ifc_file)
        
        floors_spaces = [(r.RelatingObject, r.RelatedObjects) for r in
                         ifc.by_type('IfcRelAggregates') if
                         r.RelatingObject.is_a('IfcBuildingStorey')]
        rel_space_boundary = ifc.by_type('IfcRelSpaceBoundary')
        data = {}
        for (floor, spaces) in floors_spaces:
            data[floor.Name] = {
                'spacesInfos':    spaces_infos(spaces),
                'connectionMap':  connection_map(spaces),
                'spacesPolygons': spaces_polygons(spaces, rel_space_boundary),
                'doorsLocations': doors_locations(spaces, rel_space_boundary)
            }
        return json.dumps(data)
    
    
    @classmethod
    def validate_ifc_file(cls, file):
        print("validation ifc file")
        return True
    
    
    def to_dict(self):
        return dict(
            id=self.pk,
            name=self.name,
            graph=json.loads(self.graph),
            filePath=self.filePath
        )



class PositionModel(models.Model):
    ifc = models.ForeignKey(IfcModel, on_delete=models.CASCADE)
    floor = models.CharField(max_length=100)
    x = models.DecimalField(max_digits=20, decimal_places=2)
    y = models.DecimalField(max_digits=20, decimal_places=2)
    
    
    def to_dict(self):
        return dict(
            id=self.pk,
            ifc=self.ifc.id,
            floor=self.floor,
            x=self.x,
            y=self.y
        )
