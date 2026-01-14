import argparse
import mrcfile
import os
import numpy as np
import json
import pathlib
from typing import Union


def parse_args():
    parser = argparse.ArgumentParser(description="CCP-EM MRC parse")
    parser.add_argument(
        "-m",
        "--map",
        required=True,
        help="Input map (MRC)",
    )
    parser.add_argument(
        "-odir",
        "--odir",
        required=False,
        default=None,
        help="Output directory",
    )

    return parser.parse_args()


def get_mrc_header_dataparameters(
    mapfile: Union[str, pathlib.Path], outdir: Union[str, pathlib.Path, None] = None
):
    map_parameters = {}
    with mrcfile.open(mapfile, mode="r", permissive=True) as mrc:
        map_parameters["nx"] = mrc.header.nx.item()
        map_parameters["ny"] = mrc.header.ny.item()
        map_parameters["nz"] = mrc.header.nz.item()
        map_parameters["nxstart"] = mrc.header.nxstart.item()
        map_parameters["nystart"] = mrc.header.nystart.item()
        map_parameters["nzstart"] = mrc.header.nzstart.item()
        map_parameters["originx"] = str(round(mrc.header.origin.x.item(), 3))
        map_parameters["originy"] = str(round(mrc.header.origin.y.item(), 3))
        map_parameters["originz"] = str(round(mrc.header.origin.z.item(), 3))
        map_parameters["cella"] = (
            str(round(mrc.header.cella.x.item(), 3)),
            str(round(mrc.header.cella.y.item(), 3)),
            str(round(mrc.header.cella.z.item(), 3)),
        )
        map_parameters["apix"] = (
            str(round(mrc.voxel_size.item()[0], 5)),
            str(round(mrc.voxel_size.item()[1], 5)),
            str(round(mrc.voxel_size.item()[2], 5)),
        )
        map_parameters["min"] = str(round(np.amin(mrc.data), 5))
        map_parameters["max"] = str(round(np.amax(mrc.data), 5))
        map_parameters["mean"] = str(round(np.mean(mrc.data), 5))
        map_parameters["std"] = str(round(np.std(mrc.data), 5))

        map_basename = os.path.splitext(os.path.basename(mapfile))[0]
        if outdir:
            out_json = os.path.join(outdir, map_basename + "_map_parameters.json")
        else:
            out_json = map_basename + "_map_parameters.json"

        with open(out_json, "w") as j:
            json.dump(map_parameters, j)


def main():
    args = parse_args()
    get_mrc_header_dataparameters(args.map, outdir=args.odir)


if __name__ == "__main__":
    main()
