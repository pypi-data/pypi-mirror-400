import argparse
import os
import json
from typing import Optional

from ccpem_utils.model.gemmi_model_utils import (
    GemmiModelUtils,
    set_bfactor_attributes,
)


def parse_args():
    parser = argparse.ArgumentParser(description="CCP-EM analyse B-factors")
    parser.add_argument(
        "-p",
        "--model",
        required=True,
        help="Input atomic model (.pdb, .cif)",
    )
    parser.add_argument(
        "-odir",
        "--odir",
        required=False,
        default=None,
        help="Output directory",
    )
    parser.add_argument(
        "-mid",
        "--mid",
        required=False,
        default=None,
        help="Model ID to prefix output file names",
    )

    return parser.parse_args()


def get_residue_bfactors(
    gemmiutils: GemmiModelUtils,
    modelid: str,
    outdir: Optional[str] = None,
):

    dict_bfact_dev = gemmiutils.get_avgbfact_deviation(skip_nonpoly=False)
    dict_attr: dict = {}
    max_bfact_dev = 0.0
    for model in dict_bfact_dev:
        dict_attr = {}
        for chain in dict_bfact_dev[model]:
            for res_id in dict_bfact_dev[model][chain]:
                residue_id = "_".join([model, chain, res_id])
                dict_attr[residue_id] = dict_bfact_dev[model][chain][res_id][-1]
                max_bfact_dev = max(
                    dict_bfact_dev[model][chain][res_id][1], max_bfact_dev
                )
        break
    # maximum deviation
    if "0" not in dict_bfact_dev:
        dict_bfact_dev["0"] = {}
    if "0" not in dict_bfact_dev["0"]:
        dict_bfact_dev["0"]["0"] = {}
    dict_bfact_dev["0"]["0"]["max_dev"] = [-1, max_bfact_dev]
    if outdir:
        out_json = os.path.join(outdir, modelid + "_residue_bfactors.json")
    else:
        out_json = modelid + "_residue_bfactors.json"
    with open(out_json, "w") as j:
        json.dump(dict_bfact_dev, j)
    return dict_attr


def get_residue_coordinates(
    gemmiutils: GemmiModelUtils, modelid: str, outdir: Optional[str] = None
):

    dict_ca_coord = gemmiutils.get_coordinates(atom_selection="one_per_residue")
    if outdir:
        out_json = os.path.join(outdir, modelid + "_residue_coordinates.json")
    else:
        out_json = modelid + "_residue_coordinates.json"
    with open(out_json, "w") as j:
        json.dump(dict_ca_coord, j)


def get_resolution(
    gemmiutils: GemmiModelUtils,
    modelid: str,
    outdir: Optional[str] = None,
):

    dict_resolution = {"resolution": gemmiutils.resolution}
    if outdir:
        out_json = os.path.join(outdir, modelid + "_model_info.json")
    else:
        out_json = modelid + "_model_info.json"
    with open(out_json, "w") as j:
        json.dump(dict_resolution, j)


def get_residue_names(
    gemmiutils: GemmiModelUtils,
    modelid: str,
    outdir: Optional[str] = None,
):
    gemmiutils.set_residue_types()
    dict_residue_names = gemmiutils.dict_resnames
    if outdir:
        out_json = os.path.join(outdir, modelid + "_residue_names.json")
    else:
        out_json = modelid + "_residue_names.json"
    with open(out_json, "w") as j:
        json.dump(dict_residue_names, j)


def main():
    args = parse_args()
    # read input
    modelfile = args.model
    if args.mid:
        modelid = args.mid
    else:
        modelid = os.path.splitext(os.path.basename(modelfile))[0]
    gemmiutils = GemmiModelUtils(modelfile)
    # get b-factors
    dict_attr = get_residue_bfactors(gemmiutils, modelid=modelid, outdir=args.odir)
    set_bfactor_attributes(modelfile, dict_attr, attr_name="bfactdev")
    # get coordinates
    get_residue_coordinates(gemmiutils, modelid=modelid, outdir=args.odir)
    # get resolution
    get_resolution(gemmiutils, modelid=modelid, outdir=args.odir)
    # get residue names
    get_residue_names(gemmiutils, modelid=modelid, outdir=args.odir)


if __name__ == "__main__":
    main()
