from mpldts.geometry._geometry import DTGEOMETRY
from mpldts.geometry.dt_segment import DTSegment
from mpldts.geometry.dt_frame import DTFrame
from numpy import radians, sin, cos
from pandas import DataFrame
from copy import deepcopy
import warnings

class DTSegments:
    """
    Class representing a collection of DT segements.

    Attributes
    ----------
        wheel : int
            Geometrical position within CMS.
        sector : int
            Geometrical position within CMS.
        station : int
            Geometrical position within CMS.
        segments : list
            List of segments in the collection.

    """

    def __init__(self, wheel, sector, station, segs_info=None):
        """
        Constructor of the Segments class..
        """
        # == parent DT container
        self.parent = DTFrame(DTGEOMETRY.get("rawId", wh=wheel, sec=sector, st=station))
        # == Chamber related parameters
        self.wheel = wheel
        self.sector = sector
        self.station = station

        # == Build the station
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
    def wheel(self):
        """
        Wheel position within CMS.

        :return: Wheel position.
        :rtype: int
        """
        return self._wheel

    @property
    def sector(self):
        """
        Sector position within CMS.

        :return: Sector position.
        :rtype: int
        """
        return self._sector

    @property
    def station(self):
        """
        Station Position within CMS.

        :return: Station position.
        :rtype: int
        """
        return self._station

    @property
    def segments(self):
        """
        Get all the segments in the station.

        :return: List of segments in the station.
        :rtype: list
        """
        return self._segments

    # == Setters

    @wheel.setter
    def wheel(self, value):
        """
        Set the wheel position.

        :param value: Wheel position.
        :type value: int
        :raises ValueError: If the value is not between -2 and 2.
        """
        if value < -2 or value > 2:
            raise ValueError("Wheel value must be between -2 and 2")
        self._wheel = value

    @sector.setter
    def sector(self, value):
        """
        Set the sector position.

        :param value: Sector position.
        :type value: int
        :raises ValueError: If the value is not between 1 and 14.
        """
        if value < 1 or value > 14:
            raise ValueError("Sector value must be between 1 and 14")
        else:
            self._sector = value

    @station.setter
    def station(self, value):
        """
        Set the station type.

        :param value: Station type.
        :type value: int
        :raises ValueError: If the value is not between 1 and 4.
        """
        if value < 1 or value > 4:
            raise ValueError("Station value must be between 1 and 4")
        self._station = value

    def _add_segment(self, segment):
        """
        Add a new segment to the collection.

        :param segment: Segment to be added.
        :type segment: DTSegment
        """
        self._segments.append(segment)

    def _build_segments(self, segements_info=None):
        """
        Build up the segments of the station. It creates the segments contained in the station and
        set the attributes.

        :param segments_info: It can be a dictionary, a list of dictionaries, or a pandas DataFrame 
                containing the segments attributes, they should be identified by index, should contains
                the geometrical center information, and angles. e.g. ``[{"index": 1, "x": 1.2, "y": 0, "z": 0, "phi": 30, "theta": 10, "quality": 300}, ...]``
        :type segments_info: dict, list, or pandas.DataFrame
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

        for info_item in info:
            x = info_item.pop("x", None)
            y = info_item.pop("y", None)
            z = info_item.pop("z", None)

            phi = info_item.pop("phi", None)
            theta = info_item.pop("theta", None)

            if not all(i is not None for i in [x, y, z, phi, theta]):
                raise ValueError(
                    "The drift cell information must contain the x, y, z, phi, and theta values."
                )

            _seg = DTSegment(parent=self.parent)
            _seg.number = info_item.pop("index", 0)
            _seg.local_center = (x, y, z)

            _dx, _dy, _dz = sin(radians(phi)), cos(radians(phi)), sin(radians(theta))
            _seg.direction = (_dx, _dy, _dz)

            for key, value in info_item.items():
                setattr(_seg, key, value)

            self._add_segment(_seg)

    def get_by_number(self, number):
        """
        Retrieve a segment by its number attribute.

        :param number: The number of the segment to retrieve.
        :type number: int
        :raises ValueError: If no segment with the specified number is found.
        """
        for segment in self._segments:
            if segment.number == number:
                return segment
        raise ValueError(f"No segment found with number: {number}")


