#
#     Copyright (C) 2019 CCP-EM
#
#     This code is distributed under the terms and conditions of the
#     CCP-EM Program Suite Licence Agreement as a CCP-EM Application.
#     A copy of the CCP-EM licence can be obtained by writing to the
#     CCP-EM Secretary, RAL Laboratory, Harwell, OX11 0FA, UK.

"""
Use this script to move the model to map position ignoring its origin records.
Useful if the model needs to be prepared to align with the
map without considering its origin
"""

import argparse
from ccpem_utils.model import gemmi_model_utils
from ccpem_utils.other.utils import compare_tuple
import os
import shutil
import mrcfile


def parse_args():
    parser = argparse.ArgumentParser(
        description="move associated model to align with zero or non-zero origin"
    )
    parser.add_argument(
        "-p",
        "--model",
        required=False,
        help="Input atomic model file (PDB or mmCIF/PDBx)",
    )
    parser.add_argument(
        "-use_record",
        "--use_record",
        choices=["origin", "nstart"],
        default="origin",
        help="shift model based on nstart only",
    )
    parser.add_argument(
        "-refm",
        "--refmap",
        required=False,
        help="Input reference map (MRC) whose origin will be used to shift input model",
    )
    parser.add_argument(
        "-fitted_zero",
        "--fitted_zero",
        default=False,
        action="store_true",
        help="Model is aligned against map with origin/nstart 0",
    )
    # parser.add_argument(
    #     "-fitted_nonzero",
    #     "--fitted_nonzero",
    #     default=True,
    #     action="store_false",
    #     help="Model is aligned against map with origin/nstart non-zero",
    # )
    parser.add_argument(
        "-tx",
        "--tx",
        type=float,
        help="Move tx Angstroms along X",
    )
    parser.add_argument(
        "-ty",
        "--ty",
        type=float,
        help="Move ty Angstroms along Y",
    )
    parser.add_argument(
        "-tz",
        "--tz",
        type=float,
        help="Move tz Angstroms along Z",
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
    model_input = args.model
    modelfile_id = os.path.splitext(os.path.basename(model_input))[0]
    # Find map origin
    if args.refmap:
        with mrcfile.open(args.refmap, header_only=True, permissive=True) as mrc:
            apix = mrc.voxel_size.item()
            ref_origin = mrc.header.origin.item()
            ref_nstart = (
                mrc.header.nxstart,
                mrc.header.nystart,
                mrc.header.nzstart,
            )
        # use origin
        if args.use_record == "origin":
            ox, oy, oz = ref_origin
        # use nstart
        else:
            ox, oy, oz = [ref_nstart[i] * apix[i] for i in range(len(apix))]
        # move to non-zero
        if args.fitted_zero:
            trans_vector = (ox, oy, oz)
        # move to zero origin
        else:
            trans_vector = (-ox, -oy, -oz)
    else:
        if not all([args.tx, args.ty, args.tz]):
            raise ValueError(
                "Input either a reference map or translation along X,Y,Z in Angstroms"
            )
        trans_vector = (args.tx, args.ty, args.tz)
    if args.ofile:
        shifted_model = args.ofile
    else:
        shifted_model = modelfile_id + "_shifted" + os.path.splitext(model_input)[1]
    if args.odir:
        shifted_model = os.path.join(args.odir, shifted_model)

    if not compare_tuple(trans_vector, (-0.0, -0.0, -0.0)):
        print("Translating {} by {}".format(modelfile_id, trans_vector))
        gemmiutils = gemmi_model_utils.GemmiModelUtils(model_input)
        gemmiutils.shift_coordinates(
            trans_vector=trans_vector,
            out_model_path=shifted_model,
            remove_charges=False,
        )
        gemmiutils.close()
    else:
        print("No translation required, just copying the file")
        shutil.copyfile(model_input, shifted_model)


if __name__ == "__main__":
    main()
