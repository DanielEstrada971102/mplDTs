from mpldts.geometry.am_dt_segment import AMDTSegment
from mpldts.geometry.station import Station
import numpy as np
from pandas import DataFrame
from copy import deepcopy
import warnings

class AMDTSegments:
    """
    Represents a collection of DT AM (Analytical Method) trigger primitive segments.

    Each DT AM segment is defined by its geometric center, direction, and quality, which together specify
    the segment's reference frame within a DT Station. Two segment types are considered:

    - Phi segments (:math:phi): These reside in the phi view of the DT Station. In the local coordinate system,
      the direction is given by the :math:psi angle, measured counter-clockwise from the vertical axis.
      For correlated segments (quality >= 6), the center is referenced to the geometric midpoint between super layers 1 and 3.
      For non-correlated segments (quality < 6), the vertical center aligns with the super layer where the segment is located,
      while the horizontal center is still referenced to the midpoint between super layers 1 and 3.

    - Theta segments (:math:`\theta`): Not yet implemented. These would reside in the eta view of the DT Station and are
    defined by the slope :math:`k` and z (horizontal) position.

    Attributes
    ----------
    segments : list of DTSegment
        The list of segments in this collection.
    """

    def __init__(self, segs_info=None):
        """
        Constructor of the Segments class.

        :param segs_info: Information for the segments at super layer level. Default is None. It could be a dictionary, a list of dictionaries,
                or a pandas DataFrame containing the segments attributes, they should be identified by wheel, sector, station, psi
                (or slope k), and position (x for :math:phi` and z for :math:`\theta`). 
                e.g. ``[{"wh": -1, "sc": 1, "st": 2, "psi": 33.2, "x": 12.2}, ...]``
        :type dt_info: dict, list of dict, or pandas.DataFrame.
        """

        # == Build the segments
        self._segments = []
        if segs_info is not None:
            self._build_segments(segs_info)

    def __len__(self):
        """
        Return the number of segments in the collection.

        :return: Number of segments.
        :rtype: int
        """
        return len(self._segments)

    def __getitem__(self, index):
        """
        Retrieve a segment by its index or slice.

        :param index: Index or slice of the segment(s).
        :type index: int or slice
        :return: Segment or list of segments.
        :rtype: DTSegment or list of DTSegment
        """
        return self._segments[index]

    def __iter__(self):
        """
        Iterate over all segments in the collection.

        :yield: Each segment in the collection.
        :rtype: DTSegment
        """
        return iter(self._segments)

    # == Getters

    @property
    def segments(self):
        """
        Get all the segments.

        :return: List of segments.
        :rtype: list
        """
        return self._segments

    def get_by_number(self, numbers):
        """
        Retrieve a segment by its number attribute.

        :param number: The number(s) of the segment to retrieve.
        :type number: int or list of int
        :return: Segment(s) with the specified number(s), or None if not found.
        :rtype: DTSegment or None
        """
        if isinstance(numbers, int):
            numbers = [numbers]
        return list((segment for segment in self._segments if segment.number in numbers))

    def _create_phi_segment(self, wh, sc, st, psi, x):

        _parent = Station(wh, sc, st)
        _segment = AMDTSegment(_parent)
        _segment._setup_transformer()

        _dx = -1* np.sin(np.radians(psi))
        _dz = np.cos(np.radians(psi))
        _segment.direction = (_dx, 0, _dz) # direction vector in local cords

        _segment.local_center = _segment.transformer.transform((x, 0, 0), from_frame="TPsFrame", to_frame="Station") # local center in local (station) cords
        _segment.global_center = _segment.transformer.transform(_segment.local_center, from_frame="Station", to_frame="CMS")

        return _segment

    def _create_theta_segment(self, wh, sc, st,k, z):
        pass

    def _build_segments(self, segements_info=None):
        """
        Build up the segments of the station. It creates the segments contained in the station and
        set the attributes.
        """
        if isinstance(segements_info, dict):
            info = [deepcopy(segements_info)]
        elif isinstance(segements_info, DataFrame):
            info = segements_info.to_dict(orient="records")
        elif isinstance(segements_info, list):
            info = deepcopy(segements_info)
        else:
            raise TypeError(
                "The segments information must be a dictionary, a list of dictionaries, or a pandas DataFrame."
            )

        for i, seg_info in enumerate(info):
            if any(
                key not in seg_info for key in ["wh", "sc", "st"]
            ):
                raise ValueError(
                    "Each segment information must contain 'wh', 'sc', and 'st' keys."
                )

            wh, sc, st = seg_info["wh"], seg_info["sc"], seg_info["st"]
            if all(
                key in seg_info for key in ["psi", "x"]
            ):
                # Create a phi segment
                psi, x = seg_info["psi"], seg_info["x"]
                _seg = self._create_phi_segment(wh, sc, st, psi, x)
            elif all(
                key in seg_info for key in ["k", "z"]
            ):
                # Create a theta segment
                k, z = seg_info["k"], seg_info["z"]
                warnings.warn(
                    "Theta segments are not yet implemented. "
                )
                continue
                # _seg = self._create_theta_segment(wh, sc, st, k, z)
            else:
                raise ValueError(
                    "Each segment information must contain 'q', 'psi'/'k', and 'x'/'z' keys."
                )
            _seg.number = getattr(seg_info, "index", i + 1)
            self._segments.append(_seg)

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # Example usage
    segments_info = [
        {"wh": -1, "sc": 1, "st": 2, "psi": -10.2, "x": 0},
        {"wh": -1, "sc": 1, "st": 2,"psi": 20.0, "x": 0.5}
    ]
    segments = AMDTSegments(segments_info)
    for seg in segments:
        print(seg)

    fig, axs = plt.subplots(1, 1, figsize=(5, 5))

    for seg in segments:
        axs.arrow(seg.local_center[0], seg.local_center[2], seg.direction[0] * 20, seg.direction[2]*20, color='blue')
        axs.annotate(f"Seg {seg.number}", (seg.local_center[0], seg.local_center[2]), textcoords="offset points", xytext=(0,10), ha='center')

    axs.set_xlim(-200, 200)
    axs.set_ylim(-30, 30)
    plt.show()