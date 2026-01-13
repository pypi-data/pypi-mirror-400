import corefinder as cf
import pickle

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np

    # ================= Test OverLap =================
    file_dir = "/data/shibo/CoresProject/seed1729/clump_core_data42"
    overlaps = []
    for snap in range(13, 99):
        overlap = cf.OverLap(
            snap,
            f"{file_dir}/thres30ini_overlap_result_downpixel_predict{snap}toreal{snap+1}.pickle",
        )
        # print(snap)
        overlap.filter_overlap(0.01)
        overlaps.append(overlap)

    a_: list[cf.CoreTrack] = cf.overlaps2tracks(overlaps)
    print(a_)
    new_a_: list[cf.CoreTrack] = []
    for a in a_:
        b = cf.CoreTrack([])
        cores = a.get_cores(file_dir)
        for core in cores:
            if -2 in core.thresholds:
                b.add_core((core.snapshot, int(core.internal_id)))
        if len(b.track) > 0:
            new_a_.append(b)
    print(new_a_)

    for a in a_:
        a.dump(f"{file_dir}/track_clump_snap{a.track[0][0]:03d}id{a.track[0][1]:03d}.pickle")
        
    for a in new_a_:
        a.dump(f"{file_dir}/track_core_snap{a.track[0][0]:03d}id{a.track[0][1]:03d}.pickle")
        
        
    # # ================= Test CoreTrack Load =================
    # file_dir = "/data/shibo/CoresProject/seed1234/clump_core_data"
    # with open(f"{file_dir}/track_snap047id004.pickle", "rb") as f:
    #     a: cf.CoreTrack = pickle.load(f)
    # print(a)
    # if there are same snapshots, two panels will be on the same frame
    # like [(1, 1), (1, 2), (2, 1), (2, 2), (2, 3), (3, 3), (3, 4)]
    # (1, 1) and (1, 2) are on the same frame
    # (2, 1) and (2, 2) and (2, 3) are on the same frame
    # (3, 3) and (3, 4) are on the same frame
    
    # record the location and length of the same snapshots
    # like above, [(0, 2), (2, 3), (5, 2)]
    # (0, 2) means the first two snapshots are on the same frame
    # (2, 3) means the third, forth, fifth snapshots are on the same frame
    # (5, 2) means the sixth and seventh snapshots are on the same frame
    # the length of the list should be the same as the number of frames
    
    # a = cf.CoreTrack([(47, 4), (48, 4),  (48, 2), (49, 5), (49, 5), (50, 5)])
    # temp_same = []
    # snaps, ids = zip(*a.track)
    # snap_start = 0
    # for i in range(1, len(snaps)):
    #     if snaps[i] == snaps[i-1]:
    #         temp_same.append((snap_start, i-snap_start))
    #         snap_start = i
    #         temp_same.append((snap_start-1, len(snaps)-snap_start-1))
    # print(temp_same)
    
    # b = a.get_cores(file_dir)
    # for core in b:
    #     plt.imshow(core.data(-2).sum(axis=0), origin="lower")
    #     plt.savefig(f"temp/core_snap{core.snapshot:03d}id{core.internal_id:03d}.png")
    #     plt.close()