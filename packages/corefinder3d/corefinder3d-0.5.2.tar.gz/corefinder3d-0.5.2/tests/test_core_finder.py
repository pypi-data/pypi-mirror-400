# tests/test_core_finder.py
from corefinder import SimCube, uppixel, MaskCube, convert_box_from_downpixel_to_real



if __name__ == "__main__":
    import pickle
    import time
    import numpy as np
    import h5py
    from skimage.measure import block_reduce

    # ==== basic test of printing ====#
    # simulation_data_path = "./data"
    # testSim = SimCube.load_zeus_snapshot(
    #     file_load_path=f"{simulation_data_path}/hdfaa.040", snapshot=40,
    # )
    # testSim.info()
    # print(testSim.file_load_path)
    # print(testSim)

    # ==== test of finding clumps ====#
    # simulation_data_path = "./data"
    # # load snapshot 40 and 41
    # starttime = time.time()
    # simdata1 = SimCube.load_zeus_snapshot(
    #     file_load_path=f"{simulation_data_path}/hdfaa.040",
    #     snapshot=40,
    # )
    # simdata2 = SimCube.load_zeus_snapshot(
    #     file_load_path=f"{simulation_data_path}/hdfaa.041",
    #     snapshot=41,
    # )
    # print(f"load time: {time.time()-starttime}")
    # simdata1.compute_speedup = True
    # simdata2.compute_speedup = True
    # # compute time
    # starttime = time.time()
    # tag1 = simdata1.tag_connected_volume(17.682717 * 30)
    # boxes1 = simdata1.get_box_of_tags(tag1)
    # tag1_pred = simdata1.predict_next_position(tag1, time_step=4/3)
    # print(f"compute one round time: {time.time()-starttime}")
    # starttime = time.time()
    # tag2 = simdata2.tag_connected_volume(17.682717 * 30)
    # print(f"compute single tag time: {time.time()-starttime}")
    # starttime = time.time()
    # overlap = SimCube.get_spatial_overlap(tag1_pred, tag2)
    # print(f"compute overlap time: {time.time()-starttime}")
    # # save boxes and overlap (they are dict)
    # with open(f"./data/thres30ini_snap40_boxes_coord_downpixel.pickle", "wb") as f:
    #     pickle.dump(boxes1, f)
    # with open(
    #     f"./data/thres30ini_overlap_result_downpixel_predict40toreal41.pickle", "wb"
    # ) as f:
    #     pickle.dump(overlap, f)
    # print("boxes and overlap saved")

    # ==== test of box region ====#
    # simulation_data_path = "./data"
    # # load snapshot 40 and 41
    # starttime = time.time()
    # simdata1 = SimCube.load_zeus_snapshot(
    #     file_load_path=f"{simulation_data_path}/hdfaa.040",
    #     snapshot=40,
    # )
    # print(f"load time: {time.time()-starttime}")
    # simdata1.compute_speedup = True
    # # compute time
    # starttime = time.time()
    # tag1 = simdata1.tag_connected_volume(17.682717 * 30)
    # np.save(f"./data/thres30ini_snap40_tag1.npy", tag1)
    # print(f"compute one round time: {time.time()-starttime}")
    start_time = time.time()
    # # ==== test the MaskCube ====#
    # with h5py.File(f"./data/hdfaa.040", "r") as f:
    #     density = f["gas_density"][...].T
    #     vx = f["i_velocity"][...].T
    #     vy = f["j_velocity"][...].T
    #     vz = f["k_velocity"][...].T
    #     Bx = f["i_mag_field"][...].T
    #     t = f["time"][()][0]
    # print(f"load time: {time.time()-start_time}")
    # # density = block_reduce(density, (3, 3, 3), np.mean)
    # # vx = block_reduce(vx, (3, 3, 3), np.mean)
    # # vy = block_reduce(vy, (3, 3, 3), np.mean)
    # # vz = block_reduce(vz, (3, 3, 3), np.mean)
    # # Bx = block_reduce(Bx, (3, 3, 3), np.mean)

    # phyinfo = {
    #         "pixel_size": 0.005,
    #         "boundary": "perodic",
    #         "time": t,
    #         "length_unit": "pc",
    #         "time_unit": "Myr",
    #         "value_unit": "Msun/pc^3",
    # }

    # with open("./data/thres30ini_snap40_boxes_coord_downpixel.pickle", "rb") as f:
    #     boxes = pickle.load(f)
    # # boxes_downpixeld is dict
    # boxes_real_unuse = convert_box_from_downpixel_to_real(boxes, block_size=(3, 3, 3))
    # boxes_real = boxes_real_unuse
    # Clumps: list[MaskCube] = []

    # start_time = time.time()

    # # use for-loop to loop over the boxes_real by the first 5 keys
    # for i, key in enumerate(list(boxes_real.keys())[2:4]):
    #     refpoint, size = boxes_real[key]
    #     refpoint = tuple(refpoint)
    #     size = tuple(size)
    #     data_subcube = MaskCube.get_subcube_from_rawcube(
    #         refpoint, size, density
    #     )
    #     mask1 = data_subcube > 30 * 17.682717
    #     Clump = MaskCube(
    #         data_subcube,
    #         ROI=None,
    #         masks={30 * 17.682717: mask1},
    #         refpoints={30 * 17.682717: refpoint},
    #         internal_id=key,
    #         snapshot=40,
    #         file_load_path="./data/hdfaa.040",
    #         phyinfo=phyinfo,
    #         original_shape=density.shape,
    #     )
    #     Clumps.append(Clump)

    # print(f"object creation time: {time.time()-start_time}")
    # start_time = time.time()

    # for clump in Clumps:
    #     print(f"This is clump {clump.internal_id}")
    #     print("try find larger clumps")
    #     clump.find_clump(20 * 17.682717, density)
    #     clump.info()
    #     clump.dump(f"./data/clump{clump.internal_id}.pkl")

    # print(f"find clump time: {time.time()-start_time}")
    # start_time = time.time()

    # # ==== test the MaskCube load and find core ====#
    Clumps: list[MaskCube] = []
    for i in range(2, 4):
        with open(f"./data/clump{i}.pkl", "rb") as f:
            Clumps.append(pickle.load(f))

    for clump in Clumps:
        print("=================================")
        print(f"This is clump {clump.internal_id}")
        print("before find core")
        clump.info()
        print("try find cores")
        clump.find_core(-2.0, locate_method="most dense")
        clump.find_core(-3.0)
        print("after find core")
        clump.info()
        clump.dump(f"./data/clump_core{clump.internal_id}.pkl")

    print(f"find core time: {time.time()-start_time}")
