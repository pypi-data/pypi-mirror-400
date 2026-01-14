#
#     Copyright (C) 2019 CCP-EM
#
#     This code is distributed under the terms and conditions of the
#     CCP-EM Program Suite Licence Agreement as a CCP-EM Application.
#     A copy of the CCP-EM licence can be obtained by writing to the
#     CCP-EM Secretary, RAL Laboratory, Harwell, OX11 0FA, UK.

import argparse

# import os
from ccpem_utils.map.mrcfile_utils import add_softedge


def parse_args():
    parser = argparse.ArgumentParser(description="CCP-EM model tools")
    parser.add_argument(
        "-m",
        "--map",
        required=True,
        help="Input map (MRC)",
    )
    parser.add_argument(
        "-r",
        "--reso",
        required=True,
        type=float,
        help="Input map resolution (Angstroms)",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    add_softedge(args.map, edge=6)
    # mapid = os.path.basename(os.path.splitext(args.map)[0])


if __name__ == "__main__":
    main()
