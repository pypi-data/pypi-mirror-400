#
#     Copyright (C) 2019 CCP-EM
#
#     This code is distributed under the terms and conditions of the
#     CCP-EM Program Suite Licence Agreement as a CCP-EM Application.
#     A copy of the CCP-EM licence can be obtained by writing to the
#     CCP-EM Secretary, RAL Laboratory, Harwell, OX11 0FA, UK.


import argparse
from ccpem_utils.map.mrcfile_utils import (
    get_origin_nstart,
    edit_map_origin_nstart,
)
from ccpem_utils.other.utils import compare_tuple
from pathlib import Path
import os


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "move map based on non-zero reference map origin/nstart or input "
            "origin/nstart"
        )
    )
    parser.add_argument(
        "-m",
        "--map",
        required=True,
        help="Input map (MRC)",
    )
    parser.add_argument(
        "-use_record",
        "--use_record",
        choices=["origin", "nstart", "both"],
        default="origin",
        help="shift model based on origin or nstart or both",
    )
    parser.add_argument(
        "-refm",
        "--refmap",
        required=False,
        help="Input reference map (MRC) whose origin will be used to shift input map",
    )
    parser.add_argument(
        "-ox",
        "--ox",
        type=float,
        help="Map origin coordinate along X",
    )
    parser.add_argument(
        "-oy",
        "--oy",
        type=float,
        help="Map origin coordinate along Y",
    )
    parser.add_argument(
        "-oz",
        "--oz",
        type=float,
        help="Map origin coordinate along Z",
    )
    parser.add_argument(
        "-nsx",
        "--nsx",
        type=int,
        help="Map nstart coordinate along X",
    )
    parser.add_argument(
        "-nsy",
        "--nsy",
        type=int,
        help="Map nstart coordinate along Y",
    )
    parser.add_argument(
        "-nsz",
        "--nsz",
        type=int,
        help="Map nstart coordinate along Z",
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
        "--ofile",
        required=False,
        default=None,
        help="Shifted map filename",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    map_input = args.map
    if args.ofile:
        shifted_map = args.ofile
    else:
        shifted_map = os.path.splitext(os.path.basename(map_input))[0] + "_shifted.mrc"
    if args.odir:
        shifted_map = os.path.join(args.odir, shifted_map)

    inp_origin, inp_nstart = get_origin_nstart(map_input)
    # Find map origin
    if args.refmap:
        ref_origin, ref_nstart = get_origin_nstart(args.refmap)
    else:
        ref_origin = (args.ox, args.oy, args.oz)
        ref_nstart = (args.nsx, args.nsy, args.nsz)
    # use origin
    if args.use_record == "origin":
        # same origin? just create a symlink
        if compare_tuple(inp_origin, ref_origin):
            Path(shifted_map).symlink_to(map_input)
            print(
                "Input and reference maps have same origin. Creating a "
                "symlink as output."
            )
        else:
            print("Shifting to reference map origin {}".format(ref_origin))
            edit_map_origin_nstart(
                map_input=map_input,
                new_origin=ref_origin,
                map_output=shifted_map,
            )
    # use nstart
    elif args.use_record == "nstart":
        # same nstart? just create a symlink
        if compare_tuple(inp_nstart, ref_nstart):
            Path(shifted_map).symlink_to(map_input)
            print(
                "Input and reference maps have same nstart. Creating a "
                "symlink as output."
            )
        else:
            print("Shifting to reference map origin {}".format(ref_origin))
            edit_map_origin_nstart(
                map_input=map_input,
                new_nstart=ref_nstart,
                map_output=shifted_map,
            )
    # both
    else:
        # same origin? just create a symlink
        if compare_tuple(inp_origin, ref_origin) and compare_tuple(
            inp_nstart, ref_nstart
        ):
            print(
                "Input and reference maps have same origin and nstart. Creating a "
                "symlink as output."
            )
            Path(shifted_map).symlink_to(map_input)

        else:
            print(
                "Shifting to reference map origin {} and nstart {}".format(
                    ref_origin, ref_nstart
                )
            )
            edit_map_origin_nstart(
                map_input=map_input,
                new_origin=ref_origin,
                new_nstart=ref_nstart,
                map_output=shifted_map,
            )


if __name__ == "__main__":
    main()
