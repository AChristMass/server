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



def spaces_polygons_data(spaces, rel_space_boundary):
    poly_map = {}
    x_min = x_max = y_min = y_max = None
    
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
        poly_map[space.GlobalId] = sorted(poly_map[space.GlobalId], key=lambda c: c.id())
        for i_curve in range(len(poly_map[space.GlobalId])):
            curve = poly_map[space.GlobalId][i_curve]
            for p in curve.Points:
                point = p.Coordinates[:2]
                poly_map[space.GlobalId][i_curve] = point
                x = point[0]
                y = point[1]
                if x_min is None or x < x_min:
                    x_min = x
                if x_max is None or x > x_max:
                    x_max = x
                if y_min is None or y < y_min:
                    y_min = y
                if y_max is None or y > y_max:
                    y_max = y
    return poly_map, x_min, x_max, y_min, y_max



def doors_polygons(spaces, rel_space_boundary):
    doors_polys = {}
    for rel in rel_space_boundary:
        door = rel.RelatedBuildingElement
        if rel.RelatingSpace not in spaces or door is None or not door.is_a('IfcDoor'):
            continue
        surface = rel.ConnectionGeometry.SurfaceOnRelatingElement
        if surface.is_a("IfcSurfaceOfLinearExtrusion"):
            profile = surface.SweptCurve
            doors_polys[door.GlobalId] = doors_polys.get(door.GlobalId, list())
            doors_polys[door.GlobalId].append(profile.Curve)
    for door_id in doors_polys:
        doors_polys[door_id] = sorted(doors_polys[door_id], key=lambda curve: curve.id())
        doors_polys[door_id] = [p.Coordinates[:2] for curve in doors_polys[door_id] for p in curve.Points]
    return doors_polys



def get_middle_point(points):
    total = (0, 0)
    for p in points:
        total = (total[0] + p[0], total[1] + p[1])
    return total[0] / len(points), total[1] / len(points)



def spaces_infos(spaces):
    return {space.GlobalId: {'name': space.Name} for space in spaces}
