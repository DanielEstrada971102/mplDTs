from mpldts.geometry.dt_frame import DTFrame
from mpldts.geometry.super_layer import SuperLayer
from mpldts.geometry.transforms import TransformManager
import warnings

class AMDTSegment:
    """
    A class representing a segment like object in a DT, which is simply a row that reconstruct the path of a particle traversing the DT.
    This class is designed to manage common attributes, getters, setters, and other functionalities.

    Attributes
    ----------
        parent : DTFrame (or subclass)
            The DT geometrical object parent where the segment lives.
        number : int
            Number identifier of the segment.
        local_center : tuple
            Local center coordinates (x, y, z) of the segment.
        global_center : tuple
            Global center coordinates (x, y, z) of the segment.
        direction : tuple
            Direction vector of the segment.

    """

    def __init__(self, parent: DTFrame = None):
        """
        Initialize the segment.
        """
        if parent is not None:
            self.parent = parent

    def __str__(self):
        """
        Provide a string representation of the object.

        :return: String representation of the object.
        :rtype: str
        """
        return (
            f"number: {self.number} "
            f"local_center: {self.local_center} "
            f"global_center: {self.global_center} "
            f"direction: {self.direction} "
        )

    @property
    def parent(self):
        """
        Parent container of the segment.

        :return: Parent container of the segment.
        :rtype: DTFrame (or subclass)
        """
        try:
            return self._parent
        except AttributeError:
            warnings.warn(f"This {self.__class__.__name__} instance does not have a Parent.")
            return None

    @property
    def number(self):
        """
        Number identifier of the Object.

        :return: Number of the Object.
        :rtype: int
        """
        try:
            return self._number
        except AttributeError:
            warnings.warn(
                f"This {self.__class__.__name__} instance does not have a Number assigned."
            )
            return None

    @property
    def local_center(self):
        """
        Local center coordinates of the Object.

        :return: Local center coordinates (x, y, z).
        :rtype: tuple
        """
        return self._x_local, self._y_local, self._z_local

    @property
    def direction(self):
        """
        Direction of the Object.

        :return: Direction of the object.
        :rtype: tuple
        """
        return self._direction

    @property
    def global_center(self):
        """
        Global center coordinates of the Object.

        :return: Global center coordinates (x, y, z).
        :rtype: tuple
        """
        return self._x_global, self._y_global, self._z_global

    @parent.setter
    def parent(self, parent: DTFrame):
        """
        Set the parent of the Object.

        :param parent: Parent of the Object.
        :type parent: DTFrame
        """
        if isinstance(parent, DTFrame) or issubclass(type(parent), DTFrame):
            self._parent = parent
        else:
            self._parent = None
            warnings.warn(f"Parent should be a DTFrame object, setting to None.")

    @number.setter
    def number(self, number: int):
        """
        Set the number of the Object.

        :param number: Number of the Object.
        :type number: int
        """
        self._number = number

    @local_center.setter
    def local_center(self, cords: tuple):
        """
        Set the local center coordinates of the Object.

        :param cords: Local center coordinates (x, y, z).
        :type cords: tuple
        """
        self._x_local, self._y_local, self._z_local = cords

    @global_center.setter
    def global_center(self, cords: tuple):
        """
        Set the global center coordinates of the Object.

        :param cords: Global center coordinates (x, y, z).
        :type cords: tuple
        """
        self._x_global, self._y_global, self._z_global = cords

    @direction.setter
    def direction(self, direction: tuple):
        """
        Set the direction of the Object.

        :param direction: Direction of the Object.
        :type direction: tuple
        """
        self._direction = direction

    def _setup_transformer(self):
        from numpy import array

        self.transformer = TransformManager("TPsFrame")

        self.transformer.add("Station", "CMS", transformation_matrix=self.parent.transformer.get_transformation("Station", "CMS"))

        sl_1_local_center = self.parent.super_layer(1).local_center[2]
        sl_3_local_center = self.parent.super_layer(3).local_center[2]
        mid_SLs_center_z = (sl_1_local_center + sl_3_local_center) / 2
        cell_48_x = self.parent.super_layer(1).layer(1).cell(48).local_center[0]

        TStSLsC = [cell_48_x, 0, mid_SLs_center_z]  # tranlation vector to move the center of the super layers to the origin in Station frame -> NEED TO FIX Y

        self.transformer.add("TPsFrame", "Station", translation_vector=TStSLsC)
