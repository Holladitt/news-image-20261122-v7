#!/usr/bin/env python3
"""Entrypoint for news-image-20261122 v7.

Copies the pre-rendered entry image next to this file to the output
directory. No network, no clock, no randomness: the same input always
produces the same bytes.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    dst = os.path.join(out, "entry.png")
    shutil.copyfile(SRC, dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
