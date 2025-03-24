from mpldts.geometry._geometry import DTGEOMETRY
from numpy import array, identity

class DTFrame(object):
    """
    A parent class representing any possible DT frame object, such as a DT cell, a Layer, a SuperLayer, or the whole DT.
    This class is designed to manage common attributes, getters, setters, etc.
    """

    def __init__(self, rawId= None):
        """
        Initialize the DTFrame object.

        :param rawId: Raw identifier of the DT geometrical object. If not provided, no XML geometrical \
            info will be used to initialize the instance.
        :type rawId: int, optional
        """
        if rawId:
            self.id = rawId
            self.local_center = DTGEOMETRY.get("LocalPosition", rawId=rawId)
            self.global_center = DTGEOMETRY.get("GlobalPosition", rawId=rawId)
            self.direction = DTGEOMETRY.get("NormalVector", rawId=rawId)
            self.bounds = DTGEOMETRY.get("Bounds", rawId=rawId)

    def __str__(self):
        """
        Provide a string representation of the principal DTFrame object properties.

        :return: String representation of the object.
        :rtype: str
        """
        return (
            f"id: {self.id} "
            f"number: {self.number} "
            f"local_center: {self.local_center}, "
            f"global_center: {self.global_center}, "
            f"bounds: {self.bounds}"
        )

    @property
    def id(self):
        """
        Identifier of the Object.

        :return: Identifier of the object.
        :rtype: int
        """
        return self._id

    @property
    def number(self):
        """
        Number of the Object.

        :return: Number of the Object.
        :rtype: int
        """
        return self._number

    @property
    def width(self):
        """
        Width of the Object.

        :return: Width of the object.
        :rtype: float
        """
        return self._width

    @property
    def height(self):
        """
        Height of the Object.

        :return: Height of the object.
        :rtype: float
        """
        return self._height

    @property
    def length(self):
        """
        Length of the Object.

        :return: Length of the object.
        :rtype: float
        """
        return self._length

    @property
    def bounds(self):
        """
        Space dimensions of the Object.

        :return: Space dimensions of the object.
        :rtype: tuple
        """
        return self._width, self._height, self._length

    @property
    def local_center(self):
        """
        Local center coordinates of the Object.

        :return: Local center coordinates (x, y, z).
        :rtype: tuple
        """
        return self._x_local, self._y_local, self._z_local

    @property
    def global_center(self):
        """
        Global center coordinates of the Object.

        :return: Global center coordinates (x, y, z).
        :rtype: tuple
        """
        return self._x_global, self._y_global, self._z_global

    @property
    def local_cords_at_min(self):
        """
        Local cords at the minimum coordinates of the Object. It means the lower left corner of the object.

        :return: Local cords at minimum coordinates (x, y, z).
        :rtype: tuple
        """
        x = self._x_local - self.width / 2
        y = self._y_local - self.height / 2
        z = self._z_local - self.length / 2
        return x, y, z

    @property
    def global_cords_at_min(self):
        """
        Global cords at the minimum coordinates of the Object. It means the lower left corner of the object.

        :return: Global cords at minimum coordinates (x, y, z).
        :rtype: tuple
        """
        x = self._x_global - self.width / 2
        y = self._y_global - self.height / 2
        z = self._z_global - self.length / 2
        return x, y, z

    @id.setter
    def id(self, id : int):
        """
        Set the identifier of the Object.

        :param id: Identifier of the Object.
        :type id: int
        """
        self._id = id

    @number.setter
    def number(self, number : int):
        """
        Set the number of the Object.

        :param number: Number of the Object.
        :type number: int
        """
        self._number = number

    @bounds.setter
    def bounds(self, bounds : tuple):
        """
        Set the space dimensions of the Object.

        :param bounds: Space dimensions of the Object (width, height, length).
        :type bounds: tuple
        """
        self._width, self._height, self._length = bounds

    @local_center.setter
    def local_center(self, cords : tuple):
        """
        Set the local center coordinates of the Object.

        :param cords: Local center coordinates (x, y, z).
        :type cords: tuple
        """
        self._x_local, self._y_local, self._z_local = self.transform2CMS(cords)

    @global_center.setter
    def global_center(self, cords : tuple):
        """
        Set the global center coordinates of the Object.

        :param cords: Global center coordinates (x, y, z).
        :type cords: tuple
        """
        self._x_global, self._y_global, self._z_global = cords

    def transform2(self, cords, matrix=identity(3)) -> tuple:
        """
        Transform the coordinates of the object to a new coordinate system.
        
        :param cords: The coordinates to transform.
        :type cords: tuple
        :param matrix: The transformation matrix.
        :type matrix: numpy.ndarray. Default, numpy.identity(3)
        :return: The transformed coordinates.
        :rtype: tuple
        """
        pos_array = array(cords)
        transformed_cords = matrix @ pos_array
        return tuple(float(value) for value in transformed_cords)

    def transform2CMS(self, cords: tuple) -> tuple:
        """
        Correct the coordinates to the CMS coordinate system. This method should be implemented by subclasses.

        :param cords: The coordinates to transform.
        :type cords: tuple
        :return: The corrected coordinates.
        :rtype: tuple
        """
        raise NotImplementedError("Subclasses should implement this method")

