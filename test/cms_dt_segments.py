import matplotlib.pyplot as plt
from mpldts.geometry import Station, DTSegments
from mpldts.patches import DTPatch, DTSegmentsPatch
from matplotlib.colors import BoundaryNorm, Normalize

dpi = 100  # Plot resolution

# Configure colormap and normalization for the plot
cmap = plt.get_cmap('viridis', 9)  # Ensure the colormap has 9 discrete colors
cmap.set_under('none')  # Set color for values below the minimum
digi_hit_norm = BoundaryNorm(boundaries=[0.1, 1, 2], ncolors=2, clip=False)
quality_norm = BoundaryNorm(boundaries=[0.1, 1, 2, 3, 4, 5, 6, 7, 8, 9], ncolors=9, clip=True)

# Cell appearance configuration
cells_kwargs = {
    "linewidth": .4 * 72 / dpi,
    "edgecolor": "k",
    "cmap": cmap,
    "norm": digi_hit_norm,
}

# Bounds appearance configuration
bounds_kwargs = {
    "linewidth": 72 / dpi,
    "edgecolor": "k",
    "facecolor": ["lightgray", "lightyellow", "lightpink", "lightblue"],
    "alpha": 0.3,  # Transparency
}

segs_kwargs = {
    "linewidth": 3 * 72 / dpi,
    "cmap": cmap,
    "norm": quality_norm,
    "alpha": 0.8,
}

digis_info = [
    {"sl": 2, "w": 51, "l": 4, "hit": 1},
    {"sl": 1, "w": 16, "l": 1, "hit": 1},
    {"sl": 3, "w": 19, "l": 3, "hit": 1},
    {"sl": 1, "w": 16, "l": 3, "hit": 1},
    {"sl": 2, "w": 50, "l": 1, "hit": 1},
    {"sl": 2, "w": 51, "l": 2, "hit": 1},
    {"sl": 3, "w": 19, "l": 2, "hit": 1},
    {"sl": 3, "w": 19, "l": 1, "hit": 1},
    {"sl": 3, "w": 21, "l": 4, "hit": 1},
    {"sl": 2, "w": 50, "l": 3, "hit": 1},
    { "sl": 1, "w": 17, "l": 2, "hit": 1},
    { "sl": 3, "w": 20, "l": 4, "hit": 1},
]

segments_info = [
    {"x": -33.255268, "y": 0, "z": 0, "phi": -22.0008581, "theta": 17, "quality": 7},
    {"x": -37.995766, "y": 0, "z": 0, "phi": -1.190311, "theta": 20, "quality": 1},
]


# Create figure and subplots
fig, axs = plt.subplots(1, 1, figsize=(7, 7),dpi=dpi)

# Define DT station
station = Station(wheel=2, sector=1, station=1, dt_info=digis_info)
segments = DTSegments(wheel=2, sector=1, station=1, segs_info=segments_info)


# Create patches for phi-view and eta-view
dt_patch = DTPatch(
    station, axes=axs, faceview="phi", local=True, inverted=True, vmap="hit", 
    cells_kwargs=cells_kwargs, bounds_kwargs=bounds_kwargs
)
segs_patch = DTSegmentsPatch(
    segments, axes=axs, faceview="phi", local=True, inverted=True, vmap="quality", 
    segs_kwargs=segs_kwargs
)

print(segs_patch.segments_collection.get_array())
# Add colorbar for the variable mapped to cell colors
fig.colorbar(segs_patch.segments_collection, label="Segment Quality", ax=axs, pad=0.01, shrink=0.8)

# Set axis limits for phi-view
width, height, length = station.bounds
x, y, z = station.local_center
axs.set_xlim(x - width / 2 - 5, x + width / 2 + 5)
axs.set_ylim(z - height / 2 - 5, z + height / 2 + 5)

# Add titles and labels
fig.suptitle(f"Segments in DT Station : {station.name}")
axs.set_title(r"$\phi$-view")
axs.set_xlabel("x [cm]")
axs.set_ylabel("-z [cm]")

plt.tight_layout()
plt.show()
# fig.savefig("./cms_dt_segments.svg", dpi=dpi)