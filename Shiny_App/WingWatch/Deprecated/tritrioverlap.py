import numpy as np


#orginal C-code was written here: https://raw.githubusercontent.com/erich666/jgt-code/master/Volume_08/Number_1/Guigue2003/tri_tri_intersect.c
#converted to python using ChatGPT.... Test rigorously using test_intro.py

# Epsilon coplanarity checks
USE_EPSILON_TEST = False
EPSILON = 1e-16

def FABS(x):
    return abs(x)

def CROSS(v1, v2):
    return np.cross(v1, v2)

def DOT(v1, v2):
    return np.dot(v1, v2)

def SUB(v1, v2):
    return np.subtract(v1, v2)

def SCALAR(alpha, v):
    return np.multiply(alpha, v)

def CHECKMINMAX(p1, q1, r1, p2, q2, r2):
    v1 = SUB(p2, q1)
    v2 = SUB(p1, q1)
    N1 = CROSS(v1, v2)
    v1 = SUB(q2, q1)
    if DOT(v1, N1) > 0:
        return 0
    v1 = SUB(p2, p1)
    v2 = SUB(r1, p1)
    N1 = CROSS(v1, v2)
    v1 = SUB(r2, p1)
    if DOT(v1, N1) > 0:
        return 0
    else:
        return 1

def TRITRI3D(p1, q1, r1, p2, q2, r2, dp2, dq2, dr2):
    if dp2 > 0:
        if dq2 > 0:
            return CHECKMINMAX(p1, r1, q1, r2, p2, q2)
        elif dr2 > 0:
            return CHECKMINMAX(p1, r1, q1, q2, r2, p2)
        else:
            return CHECKMINMAX(p1, q1, r1, p2, q2, r2)
    elif dp2 < 0:
        if dq2 < 0:
            return CHECKMINMAX(p1, q1, r1, r2, p2, q2)
        elif dr2 < 0:
            return CHECKMINMAX(p1, q1, r1, q2, r2, p2)
        else:
            return CHECKMINMAX(p1, r1, q1, p2, q2, r2)
    else:
        if dq2 < 0:
            if dr2 >= 0:
                return CHECKMINMAX(p1, r1, q1, q2, r2, p2)
            else:
                return CHECKMINMAX(p1, q1, r1, p2, q2, r2)
        elif dq2 > 0:
            if dr2 > 0:
                return CHECKMINMAX(p1, r1, q1, p2, q2, r2)
            else:
                return CHECKMINMAX(p1, q1, r1, q2, r2, p2)
        else:
            if dr2 > 0:
                return CHECKMINMAX(p1, q1, r1, r2, p2, q2)
            elif dr2 < 0:
                return CHECKMINMAX(p1, r1, q1, r2, p2, q2)
            else:
                return coplanarTriTri3d(p1, q1, r1, p2, q2, r2, N1)

def triTriOverlapTest3d(p1, q1, r1, p2, q2, r2):
    v1 = SUB(p2, r2)
    v2 = SUB(q2, r2)
    N2 = CROSS(v1, v2)

    v1 = SUB(p1, r2)
    dp1 = DOT(v1, N2)
    v1 = SUB(q1, r2)
    dq1 = DOT(v1, N2)
    v1 = SUB(r1, r2)
    dr1 = DOT(v1, N2)

    if USE_EPSILON_TEST:
        if FABS(dp1) < EPSILON:
            dp1 = 0
        if FABS(dq1) < EPSILON:
            dq1 = 0
        if FABS(dr1) < EPSILON:
            dr1 = 0

    if ((dp1 * dq1) > 0) and ((dp1 * dr1) > 0):
        return 0

    v1 = SUB(q1, p1)
    v2 = SUB(r1, p1)
    N1 = CROSS(v1, v2)

    v1 = SUB(p2, r1)
    dp2 = DOT(v1, N1)
    v1 = SUB(q2, r1)
    dq2 = DOT(v1, N1)
    v1 = SUB(r2, r1)
    dr2 = DOT(v1, N1)

    if USE_EPSILON_TEST:
        if FABS(dp2) < EPSILON:
            dp2 = 0
        if FABS(dq2) < EPSILON:
            dq2 = 0
        if FABS(dr2) < EPSILON:
            dr2 = 0

    if ((dp2 * dq2) > 0) and ((dp2 * dr2) > 0):
        return 0

    if dp1 > 0:
        if dq1 > 0:
            return TRITRI3D(r1, p1, q1, p2, r2, q2, dp2, dr2, dq2)
        elif dr1 > 0:
            return TRITRI3D(q1, r1, p1, p2, r2, q2, dp2, dr2, dq2)
        else:
            return TRITRI3D(p1, q1, r1, p2, q2, r2, dp2, dq2, dr2)
    elif dp1 < 0:
        if dq1 < 0:
            return TRITRI3D(r1, p1, q1, p2, q2, r2, dp2, dq2, dr2)
        elif dr1 < 0:
            return TRITRI3D(q1, r1, p1, p2, q2, r2, dp2, dq2, dr2)
        else:
            return TRITRI3D(p1, q1, r1, p2, r2, q2, dp2, dr2, dq2)
    else:
        if dq1 < 0:
            if dr1 >= 0:
                return TRITRI3D(q1, r1, p1, p2, r2, q2, dp2, dr2, dq2)
            else:
                return TRITRI3D(p1, q1, r1, p2, q2, r2, dp2, dq2, dr2)
        elif dq1 > 0:
            if dr1 > 0:
                return TRITRI3D(p1, q1, r1, p2, r2, q2, dp2, dr2, dq2)
            else:
                return TRITRI3D(q1, r1, p1, p2, q2, r2, dp2, dq2, dr2)
        else:
            if dr1 > 0:
                return TRITRI3D(r1, p1, q1, p2, q2, r2, dp2, dq2, dr2)
            elif dr1 < 0:
                return TRITRI3D(r1, p1, q1, p2, r2, q2, dp2, dr2, dq2)
            else:
                return coplanarTriTri3d(p1, q1, r1, p2, q2, r2, N1)

def coplanarTriTri3d(p1, q1, r1, p2, q2, r2, normal1):
    P1 = [0, 0]
    Q1 = [0, 0]
    R1 = [0, 0]
    P2 = [0, 0]
    Q2 = [0, 0]
    R2 = [0, 0]

    n_x = abs(normal1[0])
    n_y = abs(normal1[1])
    n_z = abs(normal1[2])

    if n_x > n_y:
        if n_x > n_z:
            i0, i1 = 1, 2
        else:
            i0, i1 = 0, 1
    else:
        if n_z > n_y:
            i0, i1 = 0, 1
        else:
            i0, i1 = 0, 2

    P1[0] = p1[i0]
    P1[1] = p1[i1]
    Q1[0] = q1[i0]
    Q1[1] = q1[i1]
    R1[0] = r1[i0]
    R1[1] = r1[i1]

    P2[0] = p2[i0]
    P2[1] = p2[i1]
    Q2[0] = q2[i0]
    Q2[1] = q2[i1]
    R2[0] = r2[i0]
    R2[1] = r2[i1]

    return triTri2D(P1, Q1, R1, P2, Q2, R2)

def triTri2D(P1, Q1, R1, P2, Q2, R2):
    if orient2D(P1, Q1, R1) < 0:
        if orient2D(P2, Q2, R2) < 0:
            return ccwTriTri2D(P1, R1, Q1, P2, R2, Q2)
        else:
            return ccwTriTri2D(P1, R1, Q1, P2, Q2, R2)
    else:
        if orient2D(P2, Q2, R2) < 0:
            return ccwTriTri2D(P1, Q1, R1, P2, R2, Q2)
        else:
            return ccwTriTri2D(P1, Q1, R1, P2, Q2, R2)

def ccwTriTri2D(P1, Q1, R1, P2, Q2, R2):
    if orient2D(P2, Q2, P1) >= 0:
        if orient2D(Q2, R2, P1) >= 0:
            if orient2D(R2, P2, P1) >= 0:
                return 1
            else:
                if orient2D(R2, P2, Q1) >= 0:
                    if orient2D(R2, Q1, P1) >= 0:
                        return 1
                    else:
                        return 0
                else:
                    return 0
        else:
            if orient2D(Q2, R2, Q1) >= 0:
                if orient2D(R2, P2, Q1) >= 0:
                    if orient2D(Q1, R2, Q2) >= 0:
                        return 1
                    else:
                        return 0
                else:
                    if orient2D(R2, P1, Q1) >= 0:
                        if orient2D(Q1, R2, Q2) >= 0:
                            return 1
                        else:
                            return 0
                    else:
                        return 0
            else:
                return 0
    else:
        if orient2D(P2, Q2, Q1) >= 0:
            if orient2D(R2, P2, P1) >= 0:
                if orient2D(Q1, R2, Q2) >= 0:
                    if orient2D(Q1, P1, R2) >= 0:
                        return 1
                    else:
                        return 0
                else:
                    return 0
            else:
                if orient2D(Q2, R2, Q1) >= 0:
                    if orient2D(P2, Q2, R1) >= 0:
                        if orient2D(Q1, P1, R2) >= 0:
                            if orient2D(R1, Q2, Q1) >= 0:
                                return 1
                            else:
                                return 0
                        else:
                            return 0
                    else:
                        return 0
                else:
                    return 0
        else:
            return 0

def orient2D(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])