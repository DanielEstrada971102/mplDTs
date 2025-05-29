from mpldts.geometry.segment import Segment
from mpldts.geometry.station import Station
import numpy as np
from pandas import DataFrame
from copy import deepcopy
import warnings

class AMDTSegments:
    """
    Represents a collection of DT AM (Analytical Method) trigger primitive segments.

    Each DT AM segment is defined by its geometric center and direction. Two segment types are considered:

    - **Phi segments**: ...
    - **Theta segments**: ...

    Attributes
    ----------
    parent : Station
        The parent station of the segments.
    segments : list of DTSegment
        The list of segments in this collection.
    """

    def __init__(self, wheel, sector, station, segs_info):
        """
        Constructor of the Segments class.

        :param segs_info: Information for the segments. It could be a dictionary, a list of dictionaries,
                or a pandas DataFrame containing the segments attributes, they should be identified by 
                e.g. ``[{"sl": 1, "psi": 33.2, "x": 12.2}, ...]``
        :type dt_info: dict, list of dict, or pandas.DataFrame.
        """
        if segs_info is None:
            raise ValueError("The segments information must be provided.")
        self.parent = Station(wheel=wheel, sector=sector, station=station)  # Parent station of the segments
        self._increase_transformer()  # Add the AM Tps transformation to the parent transformer
        # == Build the segments ==
        self._segments = []
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

    def _increase_transformer(self):
        """ Add to the parent transformer the transformation to move from the AM Trigger primitives frame to the Station frame."""
        sl_1_local_center = self.parent.super_layer(1).local_center[2]
        sl_3_local_center = self.parent.super_layer(3).local_center[2]
        mid_SLs_center_z = (sl_1_local_center + sl_3_local_center) / 2
        cell_48_x = self.parent.super_layer(1).layer(1).cell(48).local_center[0]

        TStSLsC = [cell_48_x, 0, mid_SLs_center_z]  # tranlation vector to move the center of TPs frame to the Station Frame -> NEED TO FIX Y

        self.parent.transformer.add("TPsFrame", "Station", translation_vector=TStSLsC)

    def _create_phi_segment(self, psi, x):
        _segment = Segment()

        _dx = -1* np.sin(np.radians(psi))
        _dz = np.cos(np.radians(psi))

        _direction = np.array([_dx, 0, _dz]) # direction vector in local cords
        _segment.direction = _direction / np.linalg.norm(_direction)  # normalize the direction vector
        _segment.local_center = self.parent.transformer.transform((x, 0, 0), from_frame="TPsFrame", to_frame="Station") # local center in local (station) cords
        _segment.global_center = self.parent.transformer.transform(_segment.local_center, from_frame="Station", to_frame="CMS")

        return _segment

    def _create_theta_segment(self, k, z):
        warnings.warn("Theta segments are not implemented yet.")
        return None

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
            if "sl" not in seg_info:
                raise ValueError(
                    "Each segment information must contain a 'sl' key."
                )
            sl = seg_info.pop("sl")
            if sl != 2:
                if not all( key in seg_info for key in ["psi", "x"]):
                    raise ValueError(
                        "Each phi-segment information must contain 'psi' and 'x' keys."
                    )
                # Create a phi segment
                psi, x = seg_info.pop("psi"), seg_info.pop("x")
                _seg = self._create_phi_segment(psi, x)
            else:
                if not all(key in seg_info for key in ["k", "z"]):
                    raise ValueError(
                        "Each theta-segment information must contain 'k' and 'z' keys."
                    )
                # Create a theta segment
                k, z = seg_info.pop("k"), seg_info.pop("z")
                _seg = self._create_theta_segment(k, z)
                continue  # Skip the rest of the loop for theta segments

            _seg.number = seg_info.pop("index", i + 1)

            for key, value in seg_info.items():
                setattr(_seg, key, value)

            self._segments.append(_seg)

if __name__ == "__main__":
    # Example usage
    segments_info = [
        {"sl":1, "psi": -10.2, "x": 0},
        {"sl":1, "psi": 20.0, "x": 0.5}
    ]
    segments = AMDTSegments(2, 1, 1, segments_info)
    for seg in segments:
        print(seg)
