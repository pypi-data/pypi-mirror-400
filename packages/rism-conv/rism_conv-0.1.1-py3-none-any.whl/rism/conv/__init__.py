# -*- coding: utf-8 -*-
import argparse
from pathlib import Path

from .amber import AmberConverter  # noqa: F401
from .base import get_converters


def main():
    converters = get_converters()

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--rtxt", type=Path,
                        help="RISM molecule file")

    subparsers = parser.add_subparsers(dest='format', required=True,
                                       help='format-specific help')

    for frm, conv_cls in converters.items():
        ap = subparsers.add_parser(frm, help=conv_cls.help)
        conv_cls.arguments(ap)

    args = parser.parse_args()
    conv = converters[args.format](args)
    conv.to_rtxt(args.rtxt)


if __name__ == "__main__":
    main()
