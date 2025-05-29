import warnings

class Segment:
    """
    A class representing a segment like object, which is simply a row that reconstruct the path of a particle traversing a detector.
    This class is designed to manage common attributes, getters, setters, and other functionalities.

    Attributes
    ----------
        number : int
            Number identifier of the segment.
        local_center : tuple
            Local center coordinates (x, y, z) of the segment.
        global_center : tuple
            Global center coordinates (x, y, z) of the segment.
        direction : tuple
            Direction vector of the segment.

    """

    def __init__(self):
        """
        Initialize the segment.
        """
        pass

    def __str__(self):
        """
        Provide a string representation of the object.

        :return: String representation of the object.
        :rtype: str
        """
        return (
            f"number: {self.number}, "
            f"local_center: {self.local_center}, "
            f"global_center: {self.global_center}, "
            f"direction: {self.direction} "
        )

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