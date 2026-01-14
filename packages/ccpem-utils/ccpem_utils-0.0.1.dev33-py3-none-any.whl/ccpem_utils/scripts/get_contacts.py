#
#     Copyright (C) 2019 CCP-EM
#
#     This code is distributed under the terms and conditions of the
#     CCP-EM Program Suite Licence Agreement as a CCP-EM Application.
#     A copy of the CCP-EM licence can be obtained by writing to the
#     CCP-EM Secretary, RAL Laboratory, Harwell, OX11 0FA, UK.

import argparse
from ccpem_utils.model import gemmi_model_utils


def parse_args():
    parser = argparse.ArgumentParser(description="CCP-EM model tools")
    parser.add_argument(
        "-m",
        "--model",
        required=True,
        help="Input atomic model file (PDB or mmCIF/PDBx",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # Read input
    print("Reading input model file:", args.model)
    gemmi_model_utils.get_residue_ca_coordinates(
        in_model_path=args.model, prot_resatom="CA", dist_pairs=7.0
    )


if __name__ == "__main__":
    main()
