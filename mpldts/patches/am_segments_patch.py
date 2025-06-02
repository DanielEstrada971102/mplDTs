from matplotlib.collections import LineCollection
from mpldts.geometry import AMDTSegments
from mpldts.patches.dt_patch_base import DTRelatedPatch
import warnings

class AMDTSegmentsPatch(DTRelatedPatch):
    """
    A class to visualize a 2D representation of AM Segments of a DT chamber in matplotlib context.

    Attributes:
    -----------
        segments_collection : matplotlib.collections.LineCollection
            A collection of line segments representing the segments of the station.
        segments : AMDTSegments
            The segments to be visualized. Can be any AMDTSegment or its child class, or a list of them.
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
        segments: AMDTSegments,
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
            warnings.warn("The 'eta' view is on development and may not work as expected.")
        self.vmap = vmap
        self.segments = segments
        
        self.segments_collection = LineCollection(
            [], **(segs_kwargs or {"linewidth": 0.8, "color": "k"}), **kwargs
        )

        super().__init__(
            station=segments.parent,
            axes=axes,
            faceview=faceview,
            local=local,
            inverted=inverted,
            collections=[self.segments_collection],
        )

    def _draw_collections(self):
        self._draw_segments()

    def _draw_segments(self):
        """
        Draw the segments within the Station.
        """
        paths = []
        vars = []
        for seg in self.segments:
            if self.view == "eta" and seg.sl != 2:
                continue
            if self.view == "phi" and seg.sl == 2:
                continue
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
        x, y, z = seg.local_center
        dx, dy, dz = seg.local_direction
        if seg.sl == 2:
            _, _, length = self.segments.parent.bounds
            x, y= -y , x # Invert x and y for eta view
            dx, dy= -dy, dx # Invert direction for eta view

        size = 40

        x_start = x - dx * size * 0.5
        z_start = z - dz * size * 0.5
        x_end = x + dx * size * 0.5
        z_end = z + dz * size * 0.5

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