import matplotlib.pyplot as plt
from mpldts.geometry import Station
from mpldts.patches import DTPatch
from mpldts.geometry import DTGeometry
dpi = 100  # Plot resolution
import numpy as np

# Cell appearance configuration
cells_kwargs = {
    "linewidth": .4 * 72 / dpi,
    "facecolor": "none",
    "edgecolor": "k",
}

# Create figure and subplots
fig, axs = plt.subplots(1, 2, figsize=(15, 7), dpi=dpi)
axs = axs.flatten()

# Define DT station
station = Station(wheel=-1, sector=2, station=1)

# Create patches for phi-view and eta-view
dt_patch_phi = DTPatch(
    station, axes=axs[0], faceview="phi", local=False, cells_kwargs=cells_kwargs,
)
dt_patch_z = DTPatch(
    station, axes=axs[1], faceview="eta", local=False, cells_kwargs=cells_kwargs,
)

# Set axis limits for phi-view
width, height, length = station.bounds
# x, y, z = station.local_center
# axs[0].set_xlim(x - width / 2 - 5, x + width / 2 + 5)
# axs[0].set_ylim(z - height / 2 - 5, z + height / 2 + 5)

# # Set axis limits for eta-view
# axs[1].set_xlim(y - length / 2 - 5, y + length / 2 + 5)
# axs[1].set_ylim(z - height / 2 - 5, z + height / 2 + 5)
x, y, z = station.global_center
axs[0].set_xlim(350, 500)
axs[0].set_ylim(-400,400)

# Set axis limits for eta-view
axs[1].set_xlim(-700, 0)
axs[1].set_ylim(350, 550)

# Add titles and labels
fig.suptitle(f"Local view of a DT Station : {station.name}")
axs[0].set_title(r"$\phi$-view")
axs[1].set_title(r"$\eta$-view")
axs[0].set_xlabel("x [cm]")
axs[0].set_ylabel("z [cm]")
axs[1].set_xlabel("x [cm]")
axs[1].set_ylabel("z [cm]")

fact = 1#np.sqrt(3) / np.sqrt(2)

phi = np.array(
    [
        [ -0.50000017,  -0.8660253,  353.849     ],
        [  0.8660253,   -0.50000017, 249.466     ],
        [  0.,           0.,           1.        ]
    ]
)

eta = np.array(
    [
        [   1.,            0.,         -267.75      ],
        [  -0.,           -1.,          432.94618598],
        [   0.,            0.,            1.        ]
    ]
)

for sl in station.super_layers:
    for layer in sl.layers:
        cell = layer.cell(layer._first_cell_id)
        local_center = np.array(cell.local_center)
        if sl.number != 2:
            global_center = phi @ local_center
            axs[0].scatter(global_center[0] * fact, global_center[1]*fact, marker="o", color="r" if layer.number!=1 else "yellow", s=20)
        else:
            global_center = eta @ local_center
            axs[1].scatter(global_center[2], np.sqrt(global_center[0]**2 + global_center[1]**2), marker="o", color="b" if layer.number!=1 else "yellow", s=20)
# for sl in station.super_layers:
#     for layer in sl.layers:
#         cell = layer.cell(layer._first_cell_id)
#         global_position = cell.local_center
#         print("sl:", sl.number, "l: ", layer.number, "w: ", cell.number, global_position)
#         if sl.number != 2:
#             axs[0].scatter(global_position[0], global_position[2], marker="o", color="r" if layer.number!=1 else "yellow", s=20)
#         else:
#             axs[1].scatter(global_position[0], global_position[2], marker="o", color="b" if layer.number!=1 else "yellow", s=20)

plt.tight_layout()
plt.show()
fig.savefig("./cms_dt_local_wb.svg", dpi=dpi)
