import matplotlib.pyplot as plt
import numpy as np
from gosti.pupil.pupil_grid import PupilGrid

def visualize_pupil_grid_mesh(grid: PupilGrid) -> None:
    import matplotlib.pyplot as plt

    x = grid.x_norm
    y = grid.y_norm
    m = grid.mask.astype(float)

    fig, ax = plt.subplots()
    ax.set_aspect("equal", "box")
    ax.pcolormesh(x, y, m, shading="auto")
    ax.set_xlabel("x_norm")
    ax.set_ylabel("y_norm")
    ax.set_title(f"PupilGrid: active={grid.n_active}/{grid.n_total}")
    plt.show()
