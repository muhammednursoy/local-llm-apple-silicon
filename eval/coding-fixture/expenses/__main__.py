import argparse
import sys

from .report import print_list
from .store import load


def main(argv=None):
    p = argparse.ArgumentParser(prog="expenses")
    p.add_argument("file")
    args = p.parse_args(argv)
    records = load(args.file)
    print_list(records, sys.stdout)


if __name__ == "__main__":
    main()
