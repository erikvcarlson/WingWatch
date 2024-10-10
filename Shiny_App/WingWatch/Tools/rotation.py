import numpy as np

def bearing_to_standard_angle(bearing_angle:float):
    """
    Convert an angle from bearing (measured clockwise from positive y-axis)
    to standard mathematical angle (measured counter-clockwise from positive x-axis).
    
    :param bearing_angle: Angle in degrees, measured clockwise from the positive y-axis.
    :return: Angle in degrees, measured counter-clockwise from the positive x-axis.
    """
    standard_angle = 90 - bearing_angle
    
    standard_angle = standard_angle % 360    
    
    return standard_angle

def cartesian_rotation(data_to_rotate: np.array, angle_degrees: float):
    """
    Rotate a set of 3D Cartesian coordinates by a given angle about the z axis.

    :param data_to_rotate: A numpy array of shape (n, 3) containing the coordinates to rotate.
    :param angle_degrees: The angle by which to rotate the coordinates, in degrees.
    :return: A numpy array of shape (n, 3) containing the rotated coordinates.
    """
    angle_radians = np.radians(angle_degrees)
    rotation_matrix = np.array([
        [np.cos(angle_radians), -np.sin(angle_radians),0],
        [np.sin(angle_radians), np.cos(angle_radians),0],
        [0,0,1]
    ])
    rotated_data = np.matmul(data_to_rotate, rotation_matrix.T)
    return rotated_data