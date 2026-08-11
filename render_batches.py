#!/usr/bin/env python3
"""Render SeedPills STL batches headlessly with the OpenSCAD CLI.

OpenSCAD alone is enough to design and export a grid interactively; this
script is only for automation: rendering a full set of STL batches covering
all 2048 BIP39 words (256 words per batch, 128 pills) in one go.

Usage:
    python3 render_batches.py                 # all 8 batches, 8x16 grids
    python3 render_batches.py --first 512 --count 1
    python3 render_batches.py --columns 5 --rows 5 --out stl_files

Requires the `openscad` binary on PATH (or pass --openscad /path/to/openscad).
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

WORDS_TOTAL = 2048


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--first", type=int, default=0,
                   help="first word index, 0-based (default: 0)")
    p.add_argument("--count", type=int, default=0,
                   help="number of batches to render (default: all remaining)")
    p.add_argument("--columns", type=int, default=8)
    p.add_argument("--rows", type=int, default=16)
    p.add_argument("--out", type=Path, default=Path("stl_files"))
    p.add_argument("--scad", type=Path, default=Path(__file__).with_name("seeds.scad"))
    p.add_argument("--openscad", default=shutil.which("openscad") or "openscad")
    args = p.parse_args()

    per_batch = args.columns * args.rows * 2  # words on both faces
    if WORDS_TOTAL % per_batch:
        sys.exit(f"error: {args.columns}x{args.rows} grid holds {per_batch} words, "
                 f"which does not divide {WORDS_TOTAL}; batch boundaries would split words")
    if args.first % per_batch:
        sys.exit(f"error: --first {args.first} is not a multiple of the batch size {per_batch}")

    total_batches = WORDS_TOTAL // per_batch
    start_batch = args.first // per_batch
    stop = total_batches if args.count == 0 else start_batch + args.count

    args.out.mkdir(exist_ok=True)
    for batch in range(start_batch, stop):
        first = batch * per_batch
        name = f"SeedPills_{args.columns}x{args.rows}_{first + 1:04d}_{first + per_batch:04d}.stl"
        out = args.out / name
        print(f"rendering {name} ...", flush=True)
        cmd = [args.openscad, "-o", str(out),
               "-D", f"first={first}",
               "-D", f"columns={args.columns}",
               "-D", f"rows={args.rows}",
               str(args.scad)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            sys.exit(f"openscad failed:\n{result.stderr}")
    print("done")


if __name__ == "__main__":
    main()
