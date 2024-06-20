def line_intersection(p1, p2, p3, p4):
    """
    Find the intersection of line segments p1p2 and p3p4.
    p1, p2, p3, p4 are np.array([x, y, z])
    """
    u = p2 - p1
    v = p4 - p3
    w = p1 - p3
    
    a = np.dot(u, u)
    b = np.dot(u, v)
    c = np.dot(v, v)
    d = np.dot(u, w)
    e = np.dot(v, w)
    
    denom = a * c - b * b
    if denom == 0:
        return None  # Lines are parallel
    
    sc = (b * e - c * d) / denom
    tc = (a * e - b * d) / denom
    
    if 0 <= sc <= 1 and 0 <= tc <= 1:
        intersection = p1 + sc * u
        return intersection
    else:
        return None  # No intersection within the line segments