from mpldts.geometry import Station
from mpldts.patches import DTPatch
import matplotlib.pyplot as plt

def main_global(faceview="phi"):
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    for sc in range(1, 15):
        for st in range(1, 5):
            if (sc == 13 or sc == 14) and st != 4:
                continue 
            station = Station(wheel=-2, sector=sc, station=st)
            _ = DTPatch(station, axes=ax, faceview=faceview, local=False, bounds_kwargs={"linewidth": 0.1, "facecolor": "none"}, cells_kwargs={"linewidth": 0.05, "facecolor": "none"})

    circle = plt.Circle((0, 0), 800, color="gray", alpha=0.05, edgecolor="none")
    ax.add_patch(circle)
    ax.set_title("Global view of DT Stations")
    ax.set_xlabel("x [cm]")
    ax.set_ylabel("-z [cm]")

    ax.set_xlim(-800, 800)
    ax.set_ylim(-800, 800)

    plt.show()

def main_local(faceview="phi"):
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    station = Station(wheel=1, sector=1, station=1)
    _ = DTPatch(station, axes=ax, faceview=faceview, local=False)

    for sl in station.super_layers:
        for l in sl.layers:
            for c in l.cells:
                if sl.number == 2 and l.number == 1 and c.number == 1:
                    ax.scatter(c.global_center[0], c.global_center[1], color="red") 
    xmin, ymin, zmin = station.global_cords_at_min
    ax.scatter(zmin, ymin, color="blue")
    ax.scatter(station.global_center[2], station.global_center[1], color="black")
    xmin, ymin, zmin = station.super_layer(1).global_cords_at_min
    ax.scatter(zmin, ymin, color="green")
    xmin, ymin, zmin = station.super_layer(2).global_cords_at_min
    ax.scatter(xmin, ymin, color="purple")
    xmin, ymin, zmin = station.super_layer(3).global_cords_at_min
    ax.scatter(zmin, ymin, color="orange")

    width, height, length = station.bounds
    x, y, _ = station.local_center
    if faceview == "phi":
        ax.set_xlim(x - width / 2, x + width / 2)
    else:
        ax.set_xlim(x - length / 2, x + length / 2)

    ax.set_ylim(y - height / 2, y + height / 2)
    ax.set_xlabel("x [cm]")
    ax.set_ylabel("-z [cm]")
    ax.set_title(f"Local view of a DT Station : {station.name}")

    plt.show()

if __name__ == "__main__":
    main_local(faceview="z")
    # main_global()