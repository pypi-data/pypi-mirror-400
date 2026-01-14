#
#     Copyright (C) 2019 CCP-EM
#
#     This code is distributed under the terms and conditions of the
#     CCP-EM Program Suite Licence Agreement as a CCP-EM Application.
#     A copy of the CCP-EM licence can be obtained by writing to the
#     CCP-EM Secretary, RAL Laboratory, Harwell, OX11 0FA, UK.

"""
Use this script to move the model back to map position that takes its non-zero
origin into account. Useful when the model has been moved previously to fit into the
map without considering its origin
"""

import argparse
from ccpem_utils.model import gemmi_model_utils
from ccpem_utils.other.utils import compare_tuple
from ccpem_utils.map.mrcfile_utils import get_mapobjhandle
import os
import shutil


def parse_args():
    parser = argparse.ArgumentParser(
        description="move model based on non-zero map origin"
    )
    parser.add_argument(
        "-m",
        "--map",
        required=True,
        help="Input map (MRC)",
    )
    parser.add_argument(
        "-p",
        "--model",
        required=False,
        help="Input atomic model file (PDB or mmCIF/PDBx)",
    )
    parser.add_argument(
        "-nstart_only",
        "--nstart_only",
        default=False,
        action="store_true",
        help="shift model based on nstart only",
    )
    parser.add_argument(
        "-origin_only",
        "--origin_only",
        default=False,
        action="store_true",
        help="shift model based on origin only",
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
    # Find map origin
    wrapped_mapobj = get_mapobjhandle(args.map)
    if args.nstart_only:
        trans_vector = (
            wrapped_mapobj.nstart[0] * wrapped_mapobj.apix[0],
            wrapped_mapobj.nstart[1] * wrapped_mapobj.apix[1],
            wrapped_mapobj.nstart[2] * wrapped_mapobj.apix[2],
        )
    elif args.origin_only:
        ox, oy, oz = wrapped_mapobj.origin
        trans_vector = (ox, oy, oz)
    else:
        wrapped_mapobj.fix_origin()  # if non-zero nstart and zero origin
        ox, oy, oz = wrapped_mapobj.origin
        trans_vector = (ox, oy, oz)
    if args.ofile:
        shifted_model = args.ofile
    else:
        shifted_model = (
            os.path.splitext(os.path.basename(args.model))[0]
            + "_shifted_nonzero"
            + os.path.splitext(args.model)[1]
        )
    if args.odir:
        shifted_model = os.path.join(args.odir, shifted_model)
    if not compare_tuple(trans_vector, (0.0, 0.0, 0.0)):
        gemmiutils = gemmi_model_utils.GemmiModelUtils(args.model)
        gemmiutils.shift_coordinates(
            trans_vector=trans_vector,
            out_model_path=shifted_model,
            remove_charges=False,
        )
        gemmiutils.close()
    else:
        shutil.copyfile(args.model, shifted_model)


if __name__ == "__main__":
    main()
