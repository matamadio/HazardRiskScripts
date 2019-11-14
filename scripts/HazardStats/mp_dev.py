from hazardstat import extract_stats


def apply_extract(d, shp, rst, field, stats):
    from hazardstat import extract_stats
    d.update(extract_stats([shp], [rst], field, stats))


if __name__ == '__main__':
    print("multiprocess dev")
    import os
    import multiprocess as mp
    from glob import glob
    import itertools as itools
    import pathlib
    from hazardstat import write_to_excel

    output_fn = "../../data/test.xlsx"
    shp_fns = [str(pathlib.Path(fn).resolve()) for fn in glob("../../data/*.shp")]
    rst_fns = [str(pathlib.Path(fn).resolve()) for fn in glob("../../data/*.tif")]

    field = 'OBJECTID'
    stats = ["min", "max", "mean"]
    with mp.Manager() as manager:

        # `d` is a DictProxy object shared between all processes
        # can be converted to dict for final write out
        d = manager.dict()

        with manager.Pool(processes=4) as pool:
            # Map each shapefile to a single raster
            # Then call apply_extract for each shp->raster combination
            file_combs = itools.product(*[[d], shp_fns, rst_fns, [field], [stats]])
            procs = pool.starmap_async(apply_extract, file_combs)
            procs.get()

        print("Writing results...")
        results = dict(d)
        for res, sht, cmt in results.values():
            write_to_excel(output_fn, res, sht, cmt)
        print("Finished")