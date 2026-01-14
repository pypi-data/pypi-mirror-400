import argparse
import os
from ccpem_utils.map.mrcfile_utils import bin_mrc_map

# import cProfile
# import time


def parse_args():
    parser = argparse.ArgumentParser(description="crop or pad mrc map")
    parser.add_argument(
        "-m",
        "--map",
        required=True,
        help="Input map (MRC)",
    )
    parser.add_argument(
        "-dx",
        "--dimx",
        default=0,
        type=int,
        help="New dimensions along X",
    )
    parser.add_argument(
        "-dy",
        "--dimy",
        default=0,
        type=int,
        help="New dimensions along Y",
    )
    parser.add_argument(
        "-dz",
        "--dimz",
        default=0,
        type=int,
        help="New dimensions along Z",
    )
    parser.add_argument(
        "-sx",
        "--spacing_x",
        default=0,
        type=float,
        help="New spacing along X",
    )
    parser.add_argument(
        "-sy",
        "--spacing_y",
        default=0,
        type=float,
        help="New spacing along Y",
    )
    parser.add_argument(
        "-sz",
        "--spacing_z",
        default=0,
        type=float,
        help="New spacing along Z",
    )
    parser.add_argument(
        "-mode",
        "--mode",
        required=False,
        default="fast",
        help="Choose from fast (less accurate) or slow (interpolation)",
    )
    parser.add_argument(
        "-method",
        "--method",
        required=False,
        default="interpolate",
        help="Choose from interpolate, stride or block_mean",
    )
    parser.add_argument(
        "-optimise_large",
        "--optimise_large",
        default=True,
        action="store_false",
        help="Use stride method for map size > 500**3 ?",
    )
    parser.add_argument(
        "-odir",
        "--odir",
        required=False,
        default=None,
        help="Output directory",
    )
    parser.add_argument(
        "-ofile",
        "--outfile",
        required=False,
        default=None,
        help="Output file name",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    new_dim = None
    if args.dimx and args.dimy and args.dimz:
        new_dim = (args.dimx, args.dimy, args.dimz)
    new_spacing = None
    if args.spacing_x and args.spacing_y and args.spacing_z:
        new_spacing = (args.spacing_x, args.spacing_y, args.spacing_z)
    if not new_spacing and not new_dim:
        raise ValueError("Please provide either new_dim or new_spacing")
    if args.outfile:
        outfile = args.outfile
        map_output = outfile
    else:
        map_output = os.path.splitext(args.map)[0] + "_binned.mrc"
    if args.odir:
        map_output = os.path.join(args.odir, os.path.basename(map_output))
    # start = time.time()
    bin_mrc_map(
        args.map,
        new_dim=new_dim,
        new_spacing=new_spacing,
        map_output=map_output,
        method=args.method,
        mode=args.mode,
        optimise_largemaps=args.optimise_large,
    )
    # end = time.time()
    # print("Time for binning: ", (end - start))


if __name__ == "__main__":
    main()
    # cProfile.run("main()", sort="tottime")
