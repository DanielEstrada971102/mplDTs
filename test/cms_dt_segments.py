import matplotlib.pyplot as plt
from mpldts.geometry import Station, AMDTSegments
from mpldts.patches import DTStationPatch, AMDTSegmentsPatch
from matplotlib.colors import BoundaryNorm, Normalize

dpi = 100  # Plot resolution

# Configure colormap and normalization for the plot
cmap = plt.get_cmap('viridis', 9)  # Ensure the colormap has 9 discrete colors
cmap.set_under('none')  # Set color for values below the minimum
quality_norm = BoundaryNorm(boundaries=[0.1, 1, 2, 3, 4, 5, 6, 7, 8, 9], ncolors=9, clip=True)

segs_kwargs = {
    "linewidth": 3 * 72 / dpi,
    "cmap": cmap,
    "norm": quality_norm,
}

segments_info = [
    {"index": 1, "sl": 3, "psi": -23.4, "x": -100, "q": 1},
    {"index": 2, "sl": 3, "psi": 20.5, "x": -50, "q": 2},
    {"index": 3, "sl": 3, "psi": 1.2, "x": 0, "q": 3},
    {"index": 4, "sl": 1, "psi": -10.2, "x": -15, "q": 2},
    {"index": 5, "sl": 1, "psi": -30.0, "x": -75, "q": 7},
    {"index": 6, "sl": 1, "psi": 68.3, "x": 2, "q": 8},
]


# Create figure and subplots
fig, axs = plt.subplots(1, 1, figsize=(7, 7),dpi=dpi)

# Define DT station
station = Station(wheel=2, sector=1, station=3)
segments = AMDTSegments(wheel=2, sector=1, station=3, segs_info=segments_info,)


# Create patches for phi-view and eta-view
dt_patch = DTStationPatch(station, axes=axs, faceview="phi", local=True, inverted=False)
segs_patch = AMDTSegmentsPatch(
    segments, axes=axs, faceview="phi", local=True, inverted=False, vmap="q", 
    segs_kwargs=segs_kwargs
)
for seg in segments:
    axs.annotate(
        f"TP: {seg.number}",
        xy=(seg.local_center[0], seg.local_center[2] + 0.3 * seg.number),
        fontsize=8, color="black"
    )

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