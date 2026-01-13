import corefinder as cf
import numpy as np
import pickle
import matplotlib.pyplot as plt


# core-21-01 is in clump13-08


file_dir = "/data/shibo/CoresProject/seed1729/clump_core_data42"

start_snap = 13
start_id = 8
threshold = 30 * 17.682717
type = "clump"

with open(f"{file_dir}/track_{type}_snap{start_snap:03d}id{start_id:03d}.pickle", "rb") as f:
    a: cf.CoreTrack = pickle.load(f)

snaps, ids = zip(*a.track)
reduce_snaps, count = np.unique(snaps, return_counts=True)
print(reduce_snaps, count)

cores: list[cf.MaskCube] = a.get_cores(file_dir)


canvas3d = a.get_filled_canvas3d_list(coreslist=cores, threshold=threshold)

canvas2d = [canvas.sum(axis=0) for canvas in canvas3d]



for i, canvas in enumerate(canvas2d):
    plt.imshow(canvas, origin="lower")
    plt.title(f"snap{reduce_snaps[i]:03d}-threshold{threshold}-{type}")
    plt.savefig(f"../temp/canvas_{reduce_snaps[i]:03d}.png")
    plt.close()
    print(f"canvas_{reduce_snaps[i]:03d}.png")