from mpldts.geometry.segment import Segment
from mpldts.geometry.station import Station
import numpy as np
from pandas import DataFrame
from copy import deepcopy

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

    def __init__(self, parent=None, wheel=None, sector=None, station=None, segs_info=None):
        """
        Constructor of the Segments class.

        :param wheel: The wheel number of the segments.
        :type wheel: int, optional
        :param sector: The sector number of the segments.
        :type sector: int, optional
        :param station: The station number of the segments.
        :type station: int, optional
        :param parent: The parent station of the segments. If provided, wheel, sector, and station are not required.
        :type parent: Station, optional
        :param segs_info: Information for the segments. It could be a dictionary, a list of dictionaries,
                or a pandas DataFrame containing the segments attributes, they should be identified by
                e.g. ``[{"sl": 1, "angle": 2, "position": 12.2}, ...]``
        :type segs_info: dict, list of dict, or pandas.DataFrame.
        """
        if segs_info is None:
            raise ValueError("The segments information must be provided.")

        if parent is not None:
            if not isinstance(parent, Station):
                raise TypeError("Parent must be an instance of Station.")
            self.parent = parent
        else:
            if any(i is None for i in (wheel, sector, station)):
                raise ValueError("wheel, sector, and station must be provided if parent is not given.")
            self.parent = Station(wheel=wheel, sector=sector, station=station)

        self._update_transformer()  # Add the AM Tps transformation to the parent transformer
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

    def _update_transformer(self):
        """
        Add to the parent transformer the transformation to move from the AM Trigger primitives frame
        to the Station frame. The TPs frame is defined as the geometrical center of the super layers 1 and 3.
        The transformation is added to the parent station's transformer with the name "TPsFrame".
        """
        sl1_center = np.array(self.parent.super_layer(1).local_center)
        sl3_center = np.array(self.parent.super_layer(3).local_center)
        sls_center = (sl1_center + sl3_center) / 2

        # Translation vector to move the center of TPs frame to the Station Frame
        self.parent.transformer.add("TPsFrame", "Station", translation_vector=sls_center)

    def _create_segment(self, sl, position, angle):
        """ 
        Create a segment with the given parameters.
        :param sl: The super layer number.
        :type sl: int
        :param position: The horizontal coordinate of the segment in the AM Trigger Primitive refereence frame.
        :type position: float
        :param angle: The angle of the segment in the local coordinates.
        :type angle: float
        :return: A Segment object representing the segment.
        :rtype: Segment
        """
        _segment = Segment()
        _segment.sl = sl  # Super layer number

        _dx = -1* np.sin(np.radians(angle))  # Calculate the x component of the direction vector
        _dz = np.cos(np.radians(angle))  # Calculate the z component of the direction vector

        _center = (position, 0, 0) if sl!=2 else (0, -position, 0)
        _segment.local_center = self.parent.transformer.transform(_center, from_frame="TPsFrame", to_frame="Station")# local center in station coordinates
        _segment.global_center = self.parent.transformer.transform(_segment.local_center, from_frame="Station", to_frame="CMS")  # global center in CMS coordinates

        _direction = np.array([_dx, 0, _dz]) if sl!=2 else np.array([0, -_dx,_dz]) # direction vector in local cords
        _local_direction = self.parent.transformer.transform(_direction, from_frame="TPsFrame", to_frame="Station", type="vector")  # direction in station coordinates
        _global_direction = self.parent.transformer.transform(_local_direction, from_frame="Station", to_frame="CMS", type="vector")  # direction in CMS coordinates
        #normalize the direction vectors
        _local_direction = _local_direction /np.sqrt(np.sum(_local_direction**2))
        _global_direction = _global_direction / np.sqrt(np.sum(_global_direction**2))

        # this is just to ensure that they are tuples of floats and not numpy types... (not important XD)
        _segment.local_center = tuple(float(i) for i in _segment.local_center)
        _segment.global_center = tuple(float(i) for i in _segment.global_center)
        _segment._local_direction = tuple(float(i) for i in _local_direction)
        _segment._global_direction = tuple(float(i) for i in _global_direction)

        return _segment

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
            sl = seg_info.pop("sl", None)
            angle = seg_info.pop("angle", None)
            position = seg_info.pop("position", None)

            if any(i is None for i in [sl, angle, position]):
                raise ValueError(
                    "Each segment information must contain 'sl', 'angle', and 'position' keys."
                )
            _seg = self._create_segment(sl, position, angle)
            _seg.number = seg_info.pop("index", i + 1)

            for key, value in seg_info.items():
                setattr(_seg, key, value)

            self._segments.append(_seg)

if __name__ == "__main__":
    # Example usage
    segments_info = [
        {"sl":1, "angle": -10.2, "position": 0},
        {"sl":3, "angle": 20.0, "position": 0},
        {"sl":2, "angle": 0.1, "position": 10},
    ]
    segments = AMDTSegments(2, 1, 3, segments_info)
    for seg in segments:
        print(seg)
    print(segments.parent.transformer)
