import argparse
import os
from ccpem_utils.map.mrcfile_utils import get_mapobjhandle, write_newmapobj
from ccpem_utils.map.mrc_map_utils import (
    mask_mapobj,
    threshold_mapobj,
    crop_map_grid,
    pad_map_grid,
)


def parse_args():
    parser = argparse.ArgumentParser(description="crop or pad mrc map")
    parser.add_argument(
        "-m",
        "--map",
        required=True,
        help="Input map (MRC)",
    )
    parser.add_argument(
        "-crop",
        "--crop",
        default=False,
        action="store_true",
        help="Crop input map ?",
    )
    parser.add_argument(
        "-pad",
        "--pad",
        default=False,
        action="store_true",
        help="Pad input map ?",
    )
    parser.add_argument(
        "-mask",
        "--mask",
        default=False,
        action="store_true",
        help="Mask input map ?",
    )
    parser.add_argument(
        "-contour",
        "--contour",
        default=False,
        action="store_true",
        help="Threshold input map ?",
    )
    parser.add_argument(
        "-cpx",
        "--cpx",
        default=0,
        type=int,
        help="Add/Remove slices along X",
    )
    parser.add_argument(
        "-cpy",
        "--cpy",
        default=0,
        type=int,
        help="Add/Remove slices along Y",
    )
    parser.add_argument(
        "-cpz",
        "--cpz",
        default=0,
        type=int,
        help="Add/Remove slices along Z",
    )
    parser.add_argument(
        "-ma",
        "--maskfile",
        required=False,
        help="Input mask (MRC)",
    )
    parser.add_argument(
        "-mt",
        "--mask_threshold",
        required=False,
        default=0.0,
        type=float,
        help="Mask threshold for cropping",
    )
    parser.add_argument(
        "-t",
        "--threshold",
        required=False,
        default=0.0,
        type=float,
        help="Map contour threshold",
    )
    parser.add_argument(
        "-ext",
        "--extend",
        required=False,
        default=10,
        type=int,
        help="Extend mask or contour edges on either sides along each axis ",
    )
    parser.add_argument(
        "-fill",
        "--fill_pad",
        required=False,
        default=None,
        type=float,
        help="Fill padding with this value",
    )
    parser.add_argument(
        "-cubic",
        "--out_cubic",
        default=False,
        help="Finds a cubic map grid based on maximum of input dimensions",
        action="store_true",
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
    input_mapobj = get_mapobjhandle(args.map)
    maskobj = None
    if args.maskfile:
        maskobj = get_mapobjhandle(args.maskfile)
    suffix = ""
    processed_mapobj = None
    if args.mask:
        suffix += "_masked"
        if not maskobj:
            raise ValueError("Provide mask file as input")
        processed_mapobj = mask_mapobj(input_mapobj, maskobj)
    elif args.contour:
        suffix += "_contoured"
        if not args.threshold:
            raise ValueError("Provide mask threshold")
        processed_mapobj = threshold_mapobj(input_mapobj, args.threshold)
    if args.crop:
        suffix += "_cropped"
        crop_dim = None
        if args.cpx or args.cpy or args.cpz:
            crop_dim = [args.cpx, args.cpy, args.cpz]
        processed_mapobj = crop_map_grid(
            input_mapobj,
            crop_dim=crop_dim,
            contour=args.threshold,
            ext=(args.extend, args.extend, args.extend),
            cubic=args.out_cubic,
            input_maskobj=maskobj,
            mask_thr=args.mask_threshold,
        )
    elif args.pad:
        suffix += "_padded"
        ext_dim = None
        if args.cpx or args.cpy or args.cpz:
            ext_dim = [args.cpx, args.cpy, args.cpz]
        processed_mapobj = pad_map_grid(
            input_mapobj,
            ext_dim=ext_dim,
            fill_padding=args.fill_pad,
        )
    elif not suffix:
        raise ValueError("Select atleast one operation of mask, contour, crop or pad")
    if not processed_mapobj:
        raise ValueError("Select atleast one operation of mask, contour, crop or pad")
    suffix += ".mrc"
    if args.outfile:
        outfile = args.outfile
    else:
        outfile = os.path.splitext(os.path.basename(args.map))[0]
        outfile += suffix
    if args.odir:
        map_output = os.path.join(args.odir, os.path.basename(outfile))
    else:
        map_output = outfile
    write_newmapobj(processed_mapobj, map_output=map_output)


if __name__ == "__main__":
    main()
