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

    station = Station(wheel=-2, sector=1, station=1)
    _ = DTPatch(station, axes=ax, faceview=faceview, local=True)

    width, height, _ = station.bounds
    x, y, _ = station.local_center
    ax.set_xlim(x - width / 2, x + width / 2)
    ax.set_ylim(y - height / 2, y + height / 2)
    ax.set_xlabel("x [cm]")
    ax.set_ylabel("-z [cm]")
    ax.set_title(f"Local view of a DT Station : {station.name}")

    plt.show()

if __name__ == "__main__":
    main_local()
    # main_global()