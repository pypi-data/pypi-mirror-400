import argparse
import gemmi
import numpy as np
import pandas as pd


def main(
    FOM=1.0,
    SIGF_scale=0.1,
    colin_fo="Fout",
    mtzin="nemap.mtz",
    mtzout="starting_nemap.mtz",
    spacegroup=None,
):
    # Set column FOM (W) to 1.0
    # Set column SIGF (Q) to 0.1 (=10%, default) of Fo values
    mtz = gemmi.read_mtz_file(mtzin)
    data_array = np.array(mtz, copy=True)
    data_frame = pd.DataFrame(data=data_array, columns=mtz.column_labels())
    if spacegroup is not None:
        mtz.spacegroup = gemmi.SpaceGroup(spacegroup)
    mtz.add_column("SIGF", "Q")
    data_frame["SIGF"] = SIGF_scale * data_frame[colin_fo]
    # data_frame['SIGF'] = 1.0
    mtz.add_column("FOM", "W")
    data_frame["FOM"] = FOM
    mtz.set_data(data_frame.to_numpy())
    mtz.history += ["Added columns SIGF and FOM using GEMMI."]
    mtz.write_to_file(mtzout)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-mtzin",
        "--mtzin",
        help=("Input MTZ filename"),
        type=str,
        dest="mtzin",
        default=None,
        required=True,
    )
    parser.add_argument(
        "-mtzout",
        "--mtzout",
        help=("Output MTZ filename"),
        type=str,
        dest="mtzout",
        default="starting_nemap.mtz",
        required=True,
    )
    parser.add_argument(
        "-colin_fo",
        "--colin_fo",
        help=("Fobs column label name; Default = %(default)s"),
        type=str,
        dest="colin_fo",
        default="Fout",
        required=True,
    )
    parser.add_argument(
        "-FOM",
        "--FOM",
        help=("Figure of merit value; Default = %(default)s"),
        type=float,
        dest="FOM",
        default=1.0,
        required=False,
    )
    parser.add_argument(
        "-SIGF_scale",
        "--SIGF_scale",
        help=("Scale for SIGF values, Default = 0.1 (10%% of Fo values)."),
        type=float,
        dest="SIGF_scale",
        default=0.1,
        required=False,
    )
    parser.add_argument(
        "-spacegroup",
        "--spacegroup",
        help=("Set spacegroup, e.g. P1"),
        type=str,
        dest="spacegroup",
        default=None,
        required=False,
    )
    args = parser.parse_args()
    main(
        FOM=args.FOM,
        SIGF_scale=args.SIGF_scale,
        colin_fo=args.colin_fo,
        mtzin=args.mtzin,
        mtzout=args.mtzout,
        spacegroup=args.spacegroup,
    )
