from pydoc import locate
from corefinder import MaskCube, CoreCube
import pickle

if __name__ == "__main__":
    i = 2
    with open(f"./data/clump_core{i}.pkl", "rb") as f:
        Clump: MaskCube = pickle.load(f)

    Clump.info()

    extra_data = {"Vx": 0 * Clump._data}
    core: CoreCube = CoreCube(
        Clump._data,
        extra_data,
        Clump._mask,
        Clump.masks,
        Clump.refpoints,
        Clump.internal_id,
        Clump.snapshot,
        Clump.phyinfo,
        original_shape = Clump.original_shape,
        file_load_path = Clump.file_load_path,
    )

    # core.info()
    core.find_core(-2.5, parental_threshold=353.65434, locate_method="most dense")
    # core.find_core(-2.5, parental_threshold=353.65434)
    core.info()
    a = core.data(threshold=-2.5, return_data_type="masked")
    print(a.sum() * 0.005**3)
    # print(core.data(threshold=-2.5, return_data_type="masked").sum()*0.005**3)
    # Vx = core.data(-2, dataset_name="Vx")
    # print((Vx == 0).all())
    
    # # save core
    # core.dump(f"./data/core{i}.pkl")
        
    # # load core
    # with open(f"./data/core{i}.pkl", "rb") as f:
    #     core2 = pickle.load(f)
        
    # core2.info()
    
    # # check if the two cores are the same
    # # == operator needs to be implemented in the class by 
    # # comparing the attributes that define the core
    # print(core == core2)