from matplotlib.collections import LineCollection
from matplotlib.transforms import Affine2D
from mpldts.geometry import DTSegments
from math import atan2, degrees

class DTSegmentsPatch:
    """
    A class to visualize a 2D representation of DT Segments in matplotlib context.

    Attributes:
    -----------
        segments_collection : matplotlib.collections.LineCollection
            A collection of line segments representing the segments of the station.
        segments : DTSegments
            The segments to be visualized. Can be any DTSegment or its child class, or a list of them.
        axes : matplotlib.axes.Axes
            The matplotlib axes to draw the patches on.
        view : str
            The view type, either "phi" or "eta".
        local : bool
            Boolean indicating whether to use local or global coordinates.
        inverted : bool
            Boolean indicating whether to invert the view. If local is False, this will not have any effect.
        vmap : str
            The variable to map to the colormap.

    .. important::

        Be aware that this is not a child class of ``matplotlib.patches.Patch``. Instead, it creates a
        ``matplotlib.collections.LineCollection`` object to draw the segments as lines.
    """

    def __init__(
        self,
        segments: DTSegments,
        axes,
        faceview="phi",
        local=True,
        inverted=False,
        vmap="quality",
        segs_kwargs=None,
        **kwargs,
    ):
        """
        Initialize a DTSegmentsPatch instance.

        :param segments: The segments objects containing the geometry information.
        :type segments: DTSegments
        :param axes: The matplotlib axes to draw the patches on.
        :type axes: matplotlib.axes.Axes
        :param faceview: The view type, either "phi" or "eta".
        :type faceview: str, optional
        :param local: Boolean indicating whether to use local or global coordinates.
        :type local: bool, optional
        :param inverted: Boolean indicating whether to invert the view. If local is False, this will not have any effect.
        :type inverted: bool, optional
        :param vmap: The variable to map to the colormap.
        :type vmap: str, optional
        :param segs_kwargs: Additional keyword arguments to apply to the LineCollection.
        :type segs_kwargs: dict, optional
        :return: None. Adds a collection with the line segments of a DT to the provided matplotlib axes.
        """
        if faceview == "eta":
            raise ValueError("DTSegmentsPatch only supports 'phi' view at the moment.")

        self.segments = segments
        self.axes = axes
        self.view = faceview
        self.local = local
        self.vmap = vmap
        self.inverted = (
            inverted if inverted and local else False
        )  # if global required (local = False), no inversion needed

        self.segments_collection = LineCollection(
            [], **(segs_kwargs or {"linewidth": 0.8, "color": "k"}), **kwargs
        )

        self._draw_segments()
        axes.add_collection(self.segments_collection)

        if self.inverted:
            self.invert_segments()

        if not self.local:
            self.move_to_global()

    def _draw_segments(self):
        """
        Draw the segments within the Station.
        """
        paths = []
        vars = []
        for seg in self.segments:
            path = self._create_segment(seg)
            var = getattr(seg, self.vmap, 0)

            paths.append(path)
            vars.append(var)

        self.segments_collection.set_paths(paths)
        self.segments_collection.set_array(vars)

    def _create_segment(self, seg):
        """
        Create a segment (line) for the given object.
        """
        center = seg.local_center
        direction = seg.direction
        size = seg.size()

        dx = direction[0] * size
        dy = direction[1] * size

        x_start = center[0] - dx * 0.5
        z_start = center[2] - dy * 0.5
        x_end = center[0] + dx * 0.5
        z_end = center[2] + dy * 0.5

        return [[x_start, z_start], [x_end, z_end]]

    def change_vmap(self, vmap):
        """
        Change the variable to map to the colormap.

        :param vmap: The variable to map to the colormap.
        :type vmap: str
        """
        self.vmap = vmap
        vars = [getattr(seg, self.vmap, 0) for seg in self.segments]
        self.segments_collection.set_array(vars)

    def move_to_global(self):
        """
        Move the segments to the global CMS frame.
        """
        base_transform = self.segments_collection.get_transform()
        transformation = Affine2D()

        x, y, z = self.segments.parent.global_center

        if not self.inverted:
            transformation = transformation.scale(*self._calculate_inversion_factors(self.view))

        if self.view == "phi":
            nx, ny, _ = self.segments.parent.direction
            angle = degrees(atan2(ny, nx)) + 90
            transformation = transformation.translate(x, y).rotate_deg_around(x, y, angle)

        self.segments_collection.set_transform(transformation + base_transform)

    def invert_segments(self):
        """
        Invert the segments view.
        """
        if not self.local:
            return

        self.inverted = not self.inverted
        base_transform = self.segments_collection.get_transform()

        adjustment = Affine2D().scale(*self._calculate_inversion_factors(self.view))
        self.segments_collection.set_transform(adjustment + base_transform)

    def _calculate_inversion_factors(self, view):
        """
        Calculate inversion factors based on the wheel and sector.

        :param view: The view type, either "phi" or "eta".
        :type view: str
        :return: A tuple of inversion factors.
        :rtype: tuple
        """
        if self.segments.wheel < 0:
            return (-1, -1) if view == "phi" else (1, -1)
        elif self.segments.wheel > 0:
            return  (1, -1) if view == "phi" else (-1, -1)
        else:  # self.wheel == 0
            if self.segments.sector in [1, 4, 5, 8, 9, 12, 13]:
                return (-1, -1) if view == "phi" else (1, -1)
            else:
                return (1, -1) if view == "phi" else (-1, -1)
