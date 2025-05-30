from mpldts.geometry.segment import Segment
from mpldts.geometry.station import Station
import numpy as np
from pandas import DataFrame
from copy import deepcopy
from functools import partial

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
                e.g. ``[{"sl": 1, "slope": 2, "position": 12.2}, ...]``
        :type dt_info: dict, list of dict, or pandas.DataFrame.
        """
        if segs_info is None:
            raise ValueError("The segments information must be provided.")
        self.parent = Station(wheel=wheel, sector=sector, station=station)  # Parent station of the segments
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
        to the Station frame.
        The transformation is defined as follows:
        - The z coordinate is set to the midpoint of the local centers of super layers 1 and 3.
        - The x coordinate is set to the local center of cell 48 in super layer 1, layer 1.
        - The y coordinate is set to the local center of cell 48 in super layer 2, layer 1 if it exists,
            otherwise it is set to 0.
        The transformation is added to the parent station's transformer with the name "TPsFramePhi" and "TPsFrameTheta".
        """
        sl_1_local_center = self.parent.super_layer(1).local_center[2]
        sl_3_local_center = self.parent.super_layer(3).local_center[2]
        vertical_center = (sl_1_local_center + sl_3_local_center) / 2

        horizontal_center_phi = self.parent.super_layer(1).layer(1).cell(48).local_center[0]

        sl2 =  self.parent.super_layer(2)
        if sl2 is not None:
            horizontal_center_theta = sl2.transformer.transform(sl2.layer(1).cell(48).local_center, from_frame="SuperLayer", to_frame="Station")[1]
        else:
            horizontal_center_theta = 0

        # Translation vector to move the center of TPs frame to the Station Frame
        TStTpPhi = [horizontal_center_phi, horizontal_center_theta, vertical_center]
        self.parent.transformer.add("TPsFramePhi", "Station", translation_vector=TStTpPhi)

        if sl2 is not None:
            # Translation vector to move the center of TPs frame to the Station Frame for theta segments
            TSl2TpTheta = sl2.transformer.transform(TStTpPhi, from_frame="Station", to_frame="SuperLayer")
            sl2.transformer.add("TPsFrameTheta", "SuperLayer", translation_vector=TSl2TpTheta)
            _transformation = sl2.transformer.get_transformation("TPsFrameTheta", "Station")
            self.parent.transformer.add("TPsFrameTheta", "Station", transformation_matrix=_transformation)
            
    def _create_segment(self, sl, position, slope):
        """ 
        Create a segment with the given parameters.
        :param sl: The super layer number.
        :type sl: int
        :param position: The horizontal coordinate of the segment in the AM Trigger Primitive refereence frame.
        :type position: float
        :param slope: The slope of the segment in the local coordinates.
        :type slope: float
        :return: A Segment object representing the segment.
        :rtype: Segment
        """
        _segment = Segment()
        _segment.sl = sl  # Super layer number

        _dx = -1* np.sin(np.atan2(slope, 1))  # Calculate the x component of the direction vector
        _dz = np.cos(np.atan2(slope, 1))  # Calculate the z component of the direction vector

        _segment.direction = np.array([_dx, 0, _dz]) # direction vector in local cords
        # the for loop is used to convert the numpy array to a tuple of floats
        if sl == 2:
            sl2 = self.parent.super_layer(2)
            if sl2 is not None:
                transformer = partial(sl2.transformer.transform, from_frame="TPsFrameTheta", to_frame="Station")
            else:
                raise ValueError("Super Layer 2 does not exist in this station.")
        else:
            transformer = partial(self.parent.transformer.transform, from_frame="TPsFramePhi", to_frame="Station")

        _segment.local_center = transformer((position, 0, 0))# local center in station coordinates
        _segment.direction = transformer(_segment.direction, type="vector")  # direction in station coordinates
        _segment.direction = _segment.direction /np.sqrt(np.sum(_segment.direction**2))  # normalize the direction vector
        _segment.global_center = self.parent.transformer.transform(_segment.local_center, from_frame="Station", to_frame="CMS")  # global center in CMS coordinates

        # this is just to ensure that they are tuples of floats and not numpy types... (not important XD)
        _segment.direction = tuple(float(i) for i in _segment.direction)
        _segment.local_center = tuple(float(i) for i in _segment.local_center)
        _segment.global_center = tuple(float(i) for i in _segment.global_center)

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
            slope = seg_info.pop("slope", None)
            position = seg_info.pop("position", None)

            if any(i is None for i in [sl, slope, position]):
                raise ValueError(
                    "Each segment information must contain 'sl', 'slope', and 'position' keys."
                )
            _seg = self._create_segment(sl, position, slope)
            _seg.number = seg_info.pop("index", i + 1)

            for key, value in seg_info.items():
                setattr(_seg, key, value)

            self._segments.append(_seg)

if __name__ == "__main__":
    # Example usage
    segments_info = [
        {"sl":1, "slope": -10.2, "position": 0},
        {"sl":3, "slope": 20.0, "position": 0},
        {"sl":2, "slope": 0.1, "position": 10},
    ]
    segments = AMDTSegments(2, 1, 3, segments_info)
    for seg in segments:
        print(seg)
    print(segments.parent.transformer)
