def connection_map(spaces):
    doors_dict = {}
    for space in spaces:
        boundaries = space.BoundedBy
        for boundary in boundaries:
            related = boundary.RelatedBuildingElement
            if related is None or not related.is_a("IfcDoor"):
                continue
            door = related
            if not doors_dict.get(door.GlobalId, False):
                # set value of globalId as tuple of (door, associatedSpaces)
                doors_dict[door.GlobalId] = (door, [space])
            else:
                # set space as doors associated spaces
                doors_dict[door.GlobalId][1].append(space)
    
    c_map = {}
    for door, associatedSpaces in doors_dict.values():
        door_id = door.GlobalId
        for i in range(len(associatedSpaces) - 1):
            iID = associatedSpaces[i].GlobalId
            for j in range(i + 1, len(associatedSpaces)):
                jID = associatedSpaces[j].GlobalId
                
                c_map[iID] = c_map.get(iID, {})
                c_map[iID][jID] = c_map[iID].get(jID, list())
                c_map[iID][jID].append(door_id)
                
                c_map[jID] = c_map.get(jID, {})
                c_map[jID][iID] = c_map[jID].get(iID, list())
                c_map[jID][iID].append(door_id)
    return c_map



def spaces_polygons(spaces, rel_space_boundary):
    poly_map = {}
    for bound in rel_space_boundary:
        space = bound.RelatingSpace
        if space not in spaces:
            continue
        surface = bound.ConnectionGeometry.SurfaceOnRelatingElement
        if surface.is_a("IfcSurfaceOfLinearExtrusion"):
            profile = surface.SweptCurve
            poly_map[space.GlobalId] = poly_map.get(space.GlobalId, list())
            poly_map[space.GlobalId].append(profile.Curve)
    for space in spaces:
        poly_map[space.GlobalId] = sorted(poly_map[space.GlobalId], key=lambda curve: curve.id())
        poly_map[space.GlobalId] = [p.Coordinates[:2] for curve in poly_map[space.GlobalId] for p in
                                    curve.Points]
    return poly_map



def doors_locations(spaces, rel_space_boundary):
    doors_l = {}
    for rel in rel_space_boundary:
        door = rel.RelatedBuildingElement
        if rel.RelatingSpace not in spaces or door is None or not door.is_a('IfcDoor'):
            continue
        surface = rel.ConnectionGeometry.SurfaceOnRelatingElement
        if surface.is_a("IfcSurfaceOfLinearExtrusion"):
            profile = surface.SweptCurve
            doors_l[door.GlobalId] = doors_l.get(door.GlobalId, list())
            for pt in profile.Curve.Points:
                doors_l[door.GlobalId].append(pt.Coordinates[:2])
    for doorId in doors_l:
        doors_l[doorId] = get_middle_point(doors_l[doorId])
    return doors_l



def get_middle_point(points):
    total = (0, 0)
    for p in points:
        total = (total[0] + p[0], total[1] + p[1])
    return total[0] / len(points), total[1] / len(points)



def spaces_infos(spaces):
    return {space.GlobalId: {'name': space.Name} for space in spaces}
