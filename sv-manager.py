#!/bin/python3
import os
from argparse import ArgumentParser
import subprocess as sp


def checkStatus(name: str) -> bool:
    return False


class Service:

    def __init__(self, name: str, enabled: bool):
        self.name = name
        self.enabled = enabled
        if self.enabled:
            self.online = checkStatus(self.name)
        else:
            self.online = False

    def __str__(self) -> str:
        return f'SV("{self.name}", enabled={self.enabled}, online={self.online})'


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

    availableServices = set(os.listdir(srcdir))
    enabledServices = set(os.listdir(svdir))

    services: list[Service] = []

    for sv in availableServices:
        services.append(Service(sv, sv in enabledServices))

    for sv in services:
        print(sv)


if __name__ == '__main__':
    exit(main())
