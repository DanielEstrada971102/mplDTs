from mpldts.geometry.layer import Layer
from mpldts.geometry import DTGEOMETRY, DTFrame
from numpy import array


class SuperLayer(DTFrame):
    """
    Class representing a SuperLayer.

    Attributes
    ----------
    layers : list
        List of layers in the super layer.
    parent : Station
        Parent station of the super layer.

    Others inherit from ``mpldts.geometry.DTFrame``... (e.g. id, local_center, global_center, direction, etc.)
    """

    def __init__(self, rawId, parent=None):
        """
        Constructor of the SuperLayer class.

        :param rawId: Raw identifier of the super layer.
        :type rawId: int
        :param parent: Parent station of the super layer. Default is None.
        :type parent: Station, optional
        """
        self.number = int(DTGEOMETRY.get("superLayerNumber", rawId=rawId))
        self.parent = parent
        super().__init__(rawId=rawId)
        self._layers = []

        self._build_super_layer()

    @property
    def layers(self):
        """
        Get all the layers in the super layer.

        :return: List of layers in the super layer.
        :rtype: list of Layer objects
        """
        return self._layers

    @DTFrame.number.setter
    def number(self, number):
        """
        Set the number of the super layer.

        :param number: Number of the super layer.
        :type number: int
        :raises ValueError: If the number is not between 1 and 3.
        """
        if number < 1 or number > 3:
            raise ValueError("SuperLayer number must be between 1 and 3")
        DTFrame.number.fset(self, number)

    def layer(self, layer_number):
        """
        Get a layer by its number. If the layer does not exist, it returns None.

        :param layer_number: Number of the layer.
        :type layer_number: int
        :return: Layer with the specified number.
        :rtype: Layer
        """
        return next((l for l in self.layers if l.number == layer_number), None)

    def _add_layer(self, layer):
        """
        Add a new layer to the super layer.

        :param layer: Layer to be added.
        :type layer: Layer
        """
        self.layers.append(layer)

    def transform2CMS(self, cords : tuple) -> tuple:
        """
        Correct the coordinates of the super layer to the CMS coordinate system. Bear in mind that the
        reference frame is rotated with respect to the CMS frame depending on the super layer number:

        CMS -> x: right, y: up, z: forward
        if SL == 1 or 3:
            SuperLayer -> x: right, y: forward, z: down
            That is, a rotation matrix of -90 degrees around the x-axis.

            .. math::

                R_x(-\\pi/2) = \\begin{bmatrix} 
                                    1 & 0 & 0 \\\\
                                    0 & 0 & 1 \\\\
                                    0 & -1 & 0
                                \\end{bmatrix}

        if SL == 2:
            SuperLayer -> x: backward, y: right, z: down
        
            That is, a rotation matrix of 90 degrees around the z-axis, then a rotation of -90 
            degrees around the x-axis.

            .. math::

                R_x(-\\pi/2) R_z(\\pi/2) = 
                    \\begin{bmatrix} 
                        1 & 0 & 0 \\\\
                        0 & 0 & 1 \\\\
                        0 & -1 & 0
                    \\end{bmatrix} \\cdot
                    \\begin{bmatrix} 
                        0 & -1 & 0 \\\\
                        1 & 0 & 0 \\\\
                        0 & 0 & 1
                    \\end{bmatrix}
                    = \\begin{bmatrix} 
                        0 & -1 & 0 \\\\
                        0 & 0 & 1 \\\\
                        -1 & 0 & 0
                    \\end{bmatrix}

        :param cords: Coordinates to be transformed.
        :type cords: tuple
        :return: Transformed coordinates.
        :rtype: tuple
        """

        if self.number == 1 or self.number == 3:
            matrix = array(
                [
                    [1, 0, 0],
                    [0, 0, 1],
                    [0, -1, 0]
                ]
            )
        else:
            matrix = array(
                [
                    [0, -1, 0],
                    [0, 0, 1],
                    [-1, 0, 0]
                ]
            )
        return self.transform2(cords, matrix)

    def _build_super_layer(self):
        """
        Build up the super layer. It creates the layers contained in the super layer.
        """
        for layer in DTGEOMETRY.get(rawId=self.id).iter("Layer"):
            self._add_layer(Layer(layer.get("rawId"), parent=self))


# Example usage
if __name__ == "__main__":
    super_layer = SuperLayer(rawId=589357056)
    print(super_layer)
    for layer in super_layer.layers:
        print(layer)