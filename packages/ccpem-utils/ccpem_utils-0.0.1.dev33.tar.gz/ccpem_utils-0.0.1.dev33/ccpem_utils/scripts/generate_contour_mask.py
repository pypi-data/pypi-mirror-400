import argparse
import os
from ccpem_utils.map.mrcfile_utils import save_contour_mask


def parse_args():
    parser = argparse.ArgumentParser(description="lowpass filter mrc map")
    parser.add_argument(
        "-m",
        "--map",
        required=True,
        help="Input map (MRC)",
    )
    parser.add_argument(
        "-c",
        "--contour",
        required=False,
        default=None,
        help="Contour level for mask",
    )
    parser.add_argument(
        "-odir",
        "--odir",
        required=False,
        default=None,
        help="Output directory",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    if args.odir:
        map_output = os.path.join(
            args.odir,
            os.path.splitext(os.path.basename(args.map))[0] + "_contour_mask.mrc",
        )
    save_contour_mask(args.map, contour=args.contour, map_output=map_output)


if __name__ == "__main__":
    main()
