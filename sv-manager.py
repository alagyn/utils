#!/bin/python3
import os
from argparse import ArgumentParser


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "--svdir",
        required=False,
        help="Service dir to use, defaults to $SVDIR if unspecified, or the cwd"
    )
    parser.add_argument(
        "--src",
        required=False,
        help=
        "Directory of service folders that can be symlinked to svdir, defaults to $SVSRC if unspecified"
    )

    args = parser.parse_args()

    if args.svdir is None:
        try:
            svdir = os.environ["SVDIR"]
        except KeyError:
            svdir = os.curdir
    else:
        svdir = str(args.svdir)

    if args.src is None:
        try:
            srcdir = os.environ["SVSRC"]
        except KeyError:
            print("Please set either $SVSRC or use the --src argument")
            parser.print_usage()
            return -1
    else:
        srcdir = args.src

    availableServices = os.listdir(srcdir)
    enabledServices = os.listdir(svdir)

    print(availableServices)
    print(enabledServices)


if __name__ == '__main__':
    exit(main())
