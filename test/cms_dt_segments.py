import matplotlib.pyplot as plt
from mpldts.geometry import Station, AMDTSegments
from mpldts.patches import DTStationPatch, AMSingleDTSegmentsPatch
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

segments_info = [
    {"wh": 2, "sc": 1, "st": 4, "sl": 3, "psi": -10.2, "x": 0},
    {"wh": 2, "sc": 1, "st": 4, "sl": 3, "psi": 20.0, "x": 20},
]


# Create figure and subplots
fig, axs = plt.subplots(1, 1, figsize=(7, 7),dpi=dpi)

# Define DT station
station = Station(wheel=2, sector=1, station=4)
segments = AMDTSegments(segs_info=segments_info,)


# Create patches for phi-view and eta-view
dt_patch = DTStationPatch(
    station, axes=axs, faceview="phi", local=False, inverted=True, vmap="hit", 
    cells_kwargs=cells_kwargs, bounds_kwargs=bounds_kwargs
)
segs_patch = AMSingleDTSegmentsPatch(
    segments, axes=axs, faceview="phi", local=False, inverted=True, vmap="quality", 
    segs_kwargs=segs_kwargs
)

axs.scatter(station.super_layer(1).local_center[0], station.super_layer(1).local_center[2], 
            marker="o", color="red", s=30)
axs.scatter(station.super_layer(3).local_center[0], station.super_layer(3).local_center[2],
            marker="o", color="blue", s=30)
axs.scatter(segments[0].local_center[0], segments[0].local_center[2], 
            marker="x", color="green", s=50)

# print(segs_patch.segments_collection.get_array())
# # Add colorbar for the variable mapped to cell colors
# fig.colorbar(segs_patch.segments_collection, label="Segment Quality", ax=axs, pad=0.01, shrink=0.8)

# Set axis limits for phi-view
width, height, length = station.bounds
x, y, z = station.local_center
axs.set_xlim(x - width / 2 - 5, x + width / 2 + 5)
axs.set_ylim(z - height / 2 - 5, z + height / 2 + 5)

axs.hlines(0, x - width / 2 - 5, x + width / 2 + 5, color="k", linewidth=1.5 * 72 / dpi)

# Add titles and labels
fig.suptitle(f"Segments in DT Station : {station.name}")
axs.set_title(r"$\phi$-view")
axs.set_xlabel("x [cm]")
axs.set_ylabel("-z [cm]")

plt.tight_layout()
plt.show()
# fig.savefig("./cms_dt_segments.svg", dpi=dpi)