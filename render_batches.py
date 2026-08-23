#!/usr/bin/env python3
"""Render SeedPills print plates headlessly with the OpenSCAD CLI.

OpenSCAD alone is enough to design and export a grid interactively; this
script is only for automation: rendering a full set of plates covering all
2048 BIP39 words in one go. By default each plate auto-fills a 256x256mm
bed and exports as compressed 3MF.

Usage:
    python3 render_batches.py                    # all plates, 3MF, auto grid
    python3 render_batches.py --double-sided     # 1024 pills instead of 2048
    python3 render_batches.py --format stl       # STL instead of 3MF
    python3 render_batches.py --first 324 --count 1

Requires an `openscad` binary; on macOS the OpenSCAD app bundle is
auto-detected (or pass --openscad /path/to/openscad).
"""

import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path

WORDS_TOTAL = 2048

# The Homebrew `openscad` cask (2021.01) ships a broken Qt build on Apple
# Silicon; the app bundle from `openscad@snapshot` works. Prefer PATH, then
# fall back to the standard app locations.
MACOS_APP_CANDIDATES = [
    Path("/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"),
    Path.home() / "Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD",
]


def find_openscad():
    on_path = shutil.which("openscad")
    if on_path:
        return on_path
    if platform.system() == "Darwin":
        for candidate in MACOS_APP_CANDIDATES:
            if candidate.exists():
                return str(candidate)
    return None


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--first", type=int, default=0,
                   help="first word index, 0-based (default: 0)")
    p.add_argument("--count", type=int, default=0,
                   help="number of batches to render (default: all remaining)")
    p.add_argument("--columns", type=int, default=0,
                   help="pills per row (default: 0 = fill the bed)")
    p.add_argument("--rows", type=int, default=0,
                   help="pills per column (default: 0 = fill the bed)")
    p.add_argument("--bed", default="256,256",
                   help="bed size in mm as W,H (default: 256,256 for P1S/X1C)")
    p.add_argument("--double-sided", action="store_true",
                   help="print word i+1024 on the back face of each pill")
    p.add_argument("--out", type=Path, default=Path("stl_files"))
    p.add_argument("--format", choices=["stl", "3mf"], default="stl",
                   help="part-file format (default: stl, universally supported)")
    p.add_argument("--scad", type=Path, default=Path(__file__).with_name("seeds.scad"))
    p.add_argument("--openscad", default=None,
                   help="path to the openscad binary (default: auto-detect)")
    args = p.parse_args()

    openscad = args.openscad or find_openscad()
    if not openscad:
        sys.exit("error: could not find an openscad binary; "
                 "pass --openscad /path/to/openscad")

    try:
        bed_w, bed_h = (float(v) for v in args.bed.split(","))
    except ValueError:
        sys.exit("error: --bed must be W,H in mm, e.g. 256,256")

    # Default pill pitch: 18.5 + 0.4 across, 7.5 + 0.4 down, with a 4mm
    # keep-out margin per side, the P1S 18x28mm front-left exclusion, and a
    # 20mm-wide clear strip on the right for a 20x20mm prime tower
    # zone (matches seeds.scad). If the scad defaults change, pass
    # --columns/--rows explicitly.
    margin, excl_w, excl_h, tower_w = 4, 18, 28, 20
    columns = args.columns or int(
        (bed_w - 2 * margin - excl_w - tower_w + 0.4) // 18.9)
    rows = args.rows or int((bed_h - 2 * margin - excl_h + 0.4) // 7.9)
    words_per_pill = 2 if args.double_sided else 1
    per_batch = columns * rows * words_per_pill

    # The word list does not have to divide evenly: the last plate simply
    # renders its unused slots blank (handled in seeds.scad).
    total_batches = -(-WORDS_TOTAL // per_batch)  # ceil
    start_batch = args.first // per_batch
    stop = total_batches if args.count == 0 else start_batch + args.count

    sides = "double" if args.double_sided else "single"
    print(f"grid: {columns}x{rows} = {columns * rows} pills/plate, "
          f"{total_batches} plates for {WORDS_TOTAL} words", flush=True)
    args.out.mkdir(exist_ok=True)
    for batch in range(start_batch, stop):
        first = batch * per_batch
        last = min(first + per_batch, WORDS_TOTAL)
        stem = (f"SeedPills_{sides}_{columns}x{rows}_"
                f"{first + 1:04d}_{last:04d}")
        print(f"rendering {stem} base + text ...", flush=True)
        defines = [
            "-D", f"first={first}",
            "-D", f"columns={columns}",
            "-D", f"rows={rows}",
            "-D", f"double_sided={'true' if args.double_sided else 'false'}",
        ]

        # Two ordinary files with identical coordinates are vendor-neutral.
        # Import both simultaneously as parts of one object, then assign a
        # different extruder/material to each part in the slicer.
        for part in ("base", "text"):
            out = args.out / f"{stem}_{part}.{args.format}"
            cmd = [openscad, "-o", str(out), *defines,
                   "-D", f'render_part="{part}"', str(args.scad)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                sys.exit(f"openscad failed rendering {part}:\n{result.stderr}")
    print("done")


if __name__ == "__main__":
    main()
