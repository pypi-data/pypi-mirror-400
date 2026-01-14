#
#     Copyright (C) 2019 CCP-EM
#
#     This code is distributed under the terms and conditions of the
#     CCP-EM Program Suite Licence Agreement as a CCP-EM Application.
#     A copy of the CCP-EM licence can be obtained by writing to the
#     CCP-EM Secretary, RAL Laboratory, Harwell, OX11 0FA, UK.

import argparse
import json
import os
from emmer.pdb.pdb_tools.find_wilson_cutoff import find_wilson_cutoff
from emmer.ndimage.bfactors.estimate_bfactor_map import (
    estimate_bfactor_map,
)


def parse_args():
    parser = argparse.ArgumentParser(description="CCP-EM model tools")
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
        "-ma",
        "--mask",
        required=False,
        help="Input binary mask (MRC)",
    )
    parser.add_argument(
        "-r",
        "--reso",
        required=True,
        type=float,
        help="Input map resolution (Angstroms)",
    )
    parser.add_argument(
        "-wilson_method",
        "--wilson_method",
        required=False,
        type=str,
        default="Singer",
        help="Method used to calculate wilson cutoff [Singer,rosenthal_henderson]",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    wilson_cutoff = find_wilson_cutoff(
        input_pdb=args.model, method=args.wilson_method, verbose=False
    )
    bfactor = estimate_bfactor_map(
        args.map,
        wilson_cutoff,
        fsc_cutoff=args.reso,
        return_fit=False,
        # return_amplitude=True,
        # return_fit_quality=True,
        # standard_notation=True,
    )
    dict_bfactor = {
        "bfactor": bfactor,
        "wilson_cutoff": wilson_cutoff,
        "fsc_cutoff": args.reso,
        "map": args.map,
    }
    print("Estimated B-factor is ", bfactor)
    mapid = os.path.basename(os.path.splitext(args.map)[0])
    with open(mapid + "_mapbfactor.json", "w") as j:
        json.dump(dict_bfactor, j)


if __name__ == "__main__":
    main()
