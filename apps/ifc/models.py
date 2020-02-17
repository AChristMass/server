import json

import ifcopenshell
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models


def connection_map(spaces):
    doorsDict = {}
    for space in spaces:
        boundaries = space.BoundedBy
        for boundary in boundaries:
            related = boundary.RelatedBuildingElement
            if related is None or not related.is_a("IfcDoor"):
                continue
            door = related
            if not doorsDict.get(door.GlobalId, False):
                # set value of globalId as tuple of (door, associatedSpaces)
                doorsDict[door.GlobalId] = (door, [space])
            else:
                # set space as doors associated spaces
                doorsDict[door.GlobalId][1].append(space)

    cMap = {}
    for door, associatedSpaces in doorsDict.values():
        doorId = door.GlobalId
        for i in range(len(associatedSpaces) - 1):
            iID = associatedSpaces[i].GlobalId
            for j in range(i + 1, len(associatedSpaces)):
                jID = associatedSpaces[j].GlobalId

                cMap[iID] = cMap.get(iID, {})
                cMap[iID][jID] = cMap[iID].get(jID, list())
                cMap[iID][jID].append(doorId)

                cMap[jID] = cMap.get(jID, {})
                cMap[jID][iID] = cMap[jID].get(iID, list())
                cMap[jID][iID].append(doorId)
    return cMap


def spaces_polygons(spaces, rel_space_boundary):
    polyMap = {}
    for bound in rel_space_boundary:
        space = bound.RelatingSpace
        if space not in spaces:
            continue
        surface = bound.ConnectionGeometry.SurfaceOnRelatingElement
        if surface.is_a("IfcSurfaceOfLinearExtrusion"):
            profile = surface.SweptCurve
            polyMap[space.GlobalId] = polyMap.get(space.GlobalId, list())
            polyMap[space.GlobalId].append(profile.Curve)
    for space in spaces:
        if space.GlobalId not in polyMap:
            continue
        polyMap[space.GlobalId] = sorted(polyMap[space.GlobalId], key=lambda curve: curve.id())
        polyMap[space.GlobalId] = [p.Coordinates[:2] for curve in polyMap[space.GlobalId] for p in curve.Points]
    return polyMap


def doors_locations(spaces, rel_space_boundary):
    doorsL = {}
    for rel in rel_space_boundary:
        door = rel.RelatedBuildingElement
        if rel.RelatingSpace not in spaces or door is None or not door.is_a('IfcDoor'):
            continue
        surface = rel.ConnectionGeometry.SurfaceOnRelatingElement
        if surface.is_a("IfcSurfaceOfLinearExtrusion"):
            profile = surface.SweptCurve
            doorsL[door.GlobalId] = doorsL.get(door.GlobalId, list())
            for pt in profile.Curve.Points:
                doorsL[door.GlobalId].append(pt.Coordinates[:2])
    for doorId in doorsL:
        doorsL[doorId] = get_middle_point(doorsL[doorId])
    return doorsL


def get_middle_point(points):
    total = (0, 0)
    for p in points:
        total = (total[0] + p[0], total[1] + p[1])
    return total[0] / len(points), total[1] / len(points)


def spaces_infos(spaces):
    return {space.GlobalId: {'name': space.Name} for space in spaces}


class IfcModel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    graph = JSONField(null=False, default=dict)
    filePath = models.FilePathField(path=settings.IFC_FILES_DIR)

    @classmethod
    def parse(cls, ifc_file):
        ifc = ifcopenshell.open(ifc_file)

        floors_spaces = [(r.RelatingObject, r.RelatedObjects) for r in ifc.by_type('IfcRelAggregates') if
                         r.RelatingObject.is_a('IfcBuildingStorey')]
        rel_space_boundary = ifc.by_type('IfcRelSpaceBoundary')
        data = {}
        for (floor, spaces) in floors_spaces:
            data[floor.Name] = {
                'spacesInfos': spaces_infos(spaces),
                'connectionMap': connection_map(spaces),
                'spacesPolygons': spaces_polygons(spaces, rel_space_boundary),
                'doorsLocations': doors_locations(spaces, rel_space_boundary)
            }
        return json.dumps(data)

    @classmethod
    def validate_ifc_file(cls, file):
        print("validation ifc file")
        return True

    def as_json(self):
        return dict(
            id=self.pk,
            name=self.name,
            graph=json.loads(self.graph),
            filePath=self.filePath
        )
