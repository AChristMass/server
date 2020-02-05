"""
import json
from tkinter import *
import ifcopenshell



def connectionMap(spaces):
    doorsDict = {}
    for space in spaces:
        boundaries = space.BoundedBy
        for boundary in boundaries:
            related = boundary.RelatedBuildingElement
            if related is None or not related.is_a("IfcDoor"):
                continue
            door = related
            doorId = door.GlobalId
            if not doorsDict.get(doorId, False):
                # set value of globalId as tuple of (door, associatedSpaces)
                doorsDict[doorId] = (door, [space])
            else:
                # set space as doors associated spaces
                doorsDict[doorId][1].append(space)
    
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



def spacesPolygons(spaces, relSpaceBoundary):
    polyMap = {}
    
    for bound in relSpaceBoundary:
        space = bound.RelatingSpace
        if space not in spaces:
            continue
        spaceId = space.GlobalId
        surface = bound.ConnectionGeometry.SurfaceOnRelatingElement
        if surface.is_a("IfcSurfaceOfLinearExtrusion"):
            profile = surface.SweptCurve
            polyMap[spaceId] = polyMap.get(spaceId, list())
            polyMap[spaceId].append(profile.Curve)
    
    for space in spaces:
        spaceId = space.GlobalId
        if spaceId not in polyMap:
            continue
        polyMap[spaceId] = sorted(polyMap[spaceId], key=lambda curve: curve.id())
        polyMap[spaceId] = [p.Coordinates[:2] for curve in polyMap[spaceId] for p in curve.Points]
    return polyMap



def doorsLocations(spaces, relSpaceBoundary):
    doorsL = {}
    for rel in relSpaceBoundary:
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
        doorsL[doorId] = getMiddlePoint(doorsL[doorId])
    return doorsL



def getMiddlePoint(points):
    total = (0, 0)
    for p in points:
        total = (total[0] + p[0], total[1] + p[1])
    return (total[0] / len(points), total[1] / len(points))



def getPath(connectionMap, source, target):
    path = list()
    pathFound = getPathAux(connectionMap, source, target, path, {})
    if pathFound:
        return path
    return []



def getPathAux(connectionMap, source, target, currentPath, visited):
    currentPath.append(source)
    visited[source] = True
    lastResult = []
    
    for node in connectionMap[source]:
        if node == target:
            visited[node] = True
            currentPath.append(node)
            return True
        if node in visited:
            continue
        tmpPath = list()
        tmpPath.extend(currentPath)
        if getPathAux(connectionMap, node, target, tmpPath, visited):
            currentPath.clear()
            currentPath.extend(tmpPath)
            return True
    return False



def spacesMapping(spaces):
    mapping = {}
    for space in spaces:
        mapping[space.GlobalId] = {
            'name': space.Name
        }
    return mapping



def doorsMapping(spaces, relSpaceBoundary):
    mapping = {}
    for rel in relSpaceBoundary:
        door = rel.RelatedBuildingElement
        if rel.RelatingSpace not in spaces or door is None or not door.is_a('IfcDoor'):
            continue
        mapping[door.GlobalId] = {
            'name': door.Name
        }
    return mapping



IFC_FILE = "ifcFile2.ifc"

ifc = ifcopenshell.open(IFC_FILE)

DRAW = False

FLOORS = ['00_RDC', '01_R+1']
FLOOR_TO_DRAW = 0

floorsSpaces = [(r.RelatingObject, r.RelatedObjects) for r in ifc.by_type('IfcRelAggregates') if
                r.RelatingObject.is_a('IfcBuildingStorey')]
relSpaceBoundary = ifc.by_type('IfcRelSpaceBoundary')
datas = {}
for (floor, spaces) in floorsSpaces:
    datas[floor.Name] = {
        'spacesMapping':  spacesMapping(spaces),
        'doorsMapping':   doorsMapping(spaces, relSpaceBoundary),
        'connectionMap':  connectionMap(spaces),
        'spacesPolygons': spacesPolygons(spaces, relSpaceBoundary),
        'doorsLocations': doorsLocations(spaces, relSpaceBoundary)
    }

with open("ifcDatas.json", "w") as ifcDatasFile:
    json.dump(datas, ifcDatasFile)

if not DRAW:
    exit()

### DRAWING
polygons = datas[FLOORS[FLOOR_TO_DRAW]]['spacesPolygons'].items()
points = datas[FLOORS[FLOOR_TO_DRAW]]['doorsLocations'].items()
dezoom = 50
move = 400
radius = 5
root = Tk()
root.geometry("1000x1000")

choosenSpaces = (-1, -1)



class GUI(Canvas):
    
    def __init__(self, master, *args, **kwargs):
        Canvas.__init__(self, master=master, *args, **kwargs)



canvas = GUI(root, width=1000, height=1000)



def clickspace(event):
    item_id = event.widget.find_withtag('current')[0]
    spaceName = canvas.gettags(item_id)[0][2:]
    global choosenSpaces
    if choosenSpaces[0] == -1:
        choosenSpaces = spaceName, -1
        drawall()
    elif choosenSpaces[1] == -1:
        choosenSpaces = choosenSpaces[0], spaceName
        drawall()
        choosenSpaces = (-1, -1)



def drawall():
    canvas.delete("all")
    canvas.create_text(50, 50, text=FLOORS[FLOOR_TO_DRAW])
    drawPath = choosenSpaces[0] != -1 and choosenSpaces[1] != -1
    resPath = []
    drPath = []
    if drawPath:
        cMap = datas[FLOORS[FLOOR_TO_DRAW]]['connectionMap']
        resPath = getPath(cMap, choosenSpaces[0], choosenSpaces[1])
        canvas.create_text(150, 150, text="Path of " + str(choosenSpaces) + " = " + str(resPath))
        for i in range(1, len(resPath)):
            dr1, dr2 = resPath[i - 1], resPath[i]
            drPath.append(cMap[dr1][dr2][0])
    for name, polygon in polygons:
        pts = [(p[0] / dezoom + move, -p[1] / dezoom + move) for p in polygon]
        tag = "sp" + name
        bgColor = ''
        if name in resPath:
            bgColor = 'green'
        canvas.create_polygon(pts, fill=bgColor, outline='gray', width=1, tag=tag)
        canvas.tag_bind(tag, '<ButtonPress-1>', clickspace)
    
    for door, p in points:
        p = (p[0] / dezoom + move, -p[1] / dezoom + move)
        bgColor = ''
        if door in drPath:
            bgColor = 'brown'
        canvas.create_oval(p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5, fill=bgColor)



def callback(event):
    canvas.create_text(event.x, event.y,
                       text=str(((event.x - move) * dezoom, (event.y - move) * dezoom)))



def changefloor(event):
    global FLOOR_TO_DRAW, polygons, points
    FLOOR_TO_DRAW = (FLOOR_TO_DRAW + 1) % len(FLOORS)
    polygons = datas[FLOORS[FLOOR_TO_DRAW]]['spacesPolygons'].items()
    points = datas[FLOORS[FLOOR_TO_DRAW]]['doorsLocations'].items()
    drawall()



drawall()
root.bind("<Button-1>", callback)
root.bind("<space>", changefloor)
canvas.pack()

root.mainloop()

"""