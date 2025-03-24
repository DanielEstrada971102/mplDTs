from mpldts.geometry.drift_cell import DriftCell
from mpldts.geometry import DTGEOMETRY, DTFrame
from numpy import array

class Layer(DTFrame):
    """
    Class representing a Layer.

    Attributes
    ----------
    cells : list
        List of drift cells in the layer.
    parent : Station
        Parent station of the super layer.

    Others inherit from ``mpldts.geometry.DTFrame``... (e.g. id, local_center, global_center, direction, etc.)
    """

    def __init__(self, rawId, parent=None):
        """
        Constructor of the Layer class.

        :param rawId: Raw identifier of the layer.
        :type rawId: int
        :param parent: Parent station of the super layer. Default is None.
        :type parent: Station, optional
        """
        self.number = int(DTGEOMETRY.get("layerNumber", rawId=rawId))
        self.parent = parent
        super().__init__(rawId=rawId)
        self._DriftCells = []

        self._first_cell_id = int(DTGEOMETRY.get(".//Channels//first", rawId=rawId))
        self._last_cell_id = int(DTGEOMETRY.get(".//Channels//last", rawId=rawId))

        self._build_layer()

    @property
    def cells(self):
        """
        Get all the layer's cells.

        :return: List of drift cells in the layer.
        :rtype: list of DriftCell
        """
        return self._DriftCells

    @DTFrame.number.setter
    def number(self, number):
        """
        Set the number of the layer.

        :param number: Number of the layer.
        :type number: int
        :raises ValueError: If the number is not between 1 and 4.
        """
        if number < 1 or number > 4:
            raise ValueError("Layer number must be between 1 and 4")
        DTFrame.number.fset(self, number)

    def cell(self, cell_id):
        """
        Get a layer cell by its id.

        :param cell_id: Identifier of the cell.
        :type cell_id: int
        :return: Drift cell with the specified id.
        :rtype: DriftCell
        :raises ValueError: If the cell_id is invalid.
        """
        if cell_id < self._first_cell_id or cell_id > self._last_cell_id:
            raise ValueError(f"Invalid cell id: {cell_id}")
        return self.cells[
            cell_id - self._first_cell_id
        ]  # to match the cell id with the list index

    def _add_cell(self, cell):
        """
        Add a new cell to the layer.

        :param cell: Drift cell to be added.
        :type cell: DriftCell
        """
        self.cells.append(cell)

    def transform2CMS(self, cords : tuple, parent_number=None) -> tuple:
        """
        Correct the coordinates of the layer to the CMS coordinate system. Bear in mind that the
        reference frame is rotated with respect to the CMS frame depending on the super layer number
        where the layer is located.

        CMS -> x: right, y: up, z: forward
        if parent SL == 1 or 3:
            Layer -> x: right, y: forward, z: down
            That is, a rotation matrix of -90 degrees around the x-axis.

            .. math::

                R_x(-\\pi/2) = \\begin{bmatrix} 
                                    1 & 0 & 0 \\\\
                                    0 & 0 & 1 \\\\
                                    0 & -1 & 0
                                \\end{bmatrix}

        if parent SL == 2:
            Layer -> x: backward, y: right, z: down
        
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
        :param parent_number: Parent super layer number. Default is None.
        :type parent_number: int, optional
        :return: Transformed coordinates.
        :rtype: tuple
        """

        if not self.parent:
            if not parent_number:
                raise ValueError("Parent super layer number must be provided")
            parent_number = parent_number
        else:
            parent_number = self.parent.number

        if parent_number == 1 or parent_number == 3:
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

    def _build_layer(self):
        """
        Ensemble a DT layer.
        """

        for n_cell in range(self._first_cell_id, self._last_cell_id + 1):
            cell = DriftCell(number=n_cell, parent=self)
            self._add_cell(cell)


if __name__ == "__main__":
    layer = Layer(589603840)
    print(layer)
    for cell in layer.cells:
        print(cell)
        if cell.number > 5:
            break
