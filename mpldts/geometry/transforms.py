from numpy import array, ndarray


def change_frame(point, from_frame, to_frame):
    """
    Util function to move a point from a DT reference frame to another."

    :param point: The point to move.
    :type point: tuple
    :param from_frame: The reference frame to move the point from. It could be {'SL2', 'Station', 'CMS', 'CMS2'}.
    :type from_frame: str
    :param to_frame: The reference frame to move the point to. It could be {'SL2', 'Station', 'CMS', 'CMS2'}.
    :type to_frame: str
    :return: The point in the new reference frame.

    .. note::
        At the moment only the transformation between SL2 and Station and vice versa are implemented.
    """
    M1 = array([[0, 1, 0], [-1, 0, 0], [0, 0, 1]])  # SL2 to Station: Rz(pi/2)
    # M2 = array([ # Station to CMS: Rx(-pi/2)
    #     [1, 0, 0],
    #     [0, 0, 1],
    #     [0, -1, 0]
    # ])
    # M3 = array([ # SL2 to CMS:
    #     [0, 0, -1],
    #     [-1, 0, 0],
    #     [0, -1, 0]
    # ])

    matrices = {
        ("SL2", "Station"): M1,
        ("Station", "SL2"): M1.T,
        # ("Station", "CMS"): M2,
        # ("SL2", "CMS"): M3,
        # ("CMS", "Station"): M2.T,
        # ("CMS", "SL2"): M3.T,
    }

    if from_frame == to_frame:
        return point

    if (from_frame, to_frame) not in matrices:
        raise ValueError(f"Transformation from {from_frame} to {to_frame} is not implemented yet.")

    if not isinstance(point, ndarray):
        point = array(point)

    return tuple(float(cord) for cord in matrices[(from_frame, to_frame)] @ point)
