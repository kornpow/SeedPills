#!/usr/bin/env python3
"""Render SeedPills print plates headlessly with the OpenSCAD CLI.

OpenSCAD alone is enough to design and export a grid interactively; this
script is only for automation: rendering a full set of plates covering all
2048 BIP39 words in one go. By default each plate auto-fills a 256x256mm
bed and exports paired STL files.

Usage:
    python3 render_batches.py                    # all plates, STL, auto grid
    python3 render_batches.py --double-sided     # 1024 pills instead of 2048
    python3 render_batches.py --format 3mf       # 3MF instead of STL
    python3 render_batches.py --first 324 --count 1

Requires an `openscad` binary; on macOS the OpenSCAD app bundle is
auto-detected (or pass --openscad /path/to/openscad).
"""

import argparse
import math
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree as ET

WORDS_TOTAL = 2048

# The Homebrew `openscad` cask (2021.01) ships a broken Qt build on Apple
# Silicon; the app bundle from `openscad@snapshot` works. Prefer PATH, then
# fall back to the standard app locations.
MACOS_APP_CANDIDATES = [
    Path("/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"),
    Path.home() / "Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD",
]

GRID_ECHO_RE = re.compile(r'ECHO:\s*"grid:\s*(\d+)\s*x\s*(\d+)\s*=')
CORE_NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
XML_NS = "http://www.w3.org/XML/1998/namespace"

ET.register_namespace("", CORE_NS)


def find_openscad():
    on_path = shutil.which("openscad")
    if on_path:
        return on_path
    if platform.system() == "Darwin":
        for candidate in MACOS_APP_CANDIDATES:
            if candidate.exists():
                return str(candidate)
    return None


def read_grid(openscad, scad, bed_w, bed_h, columns, rows):
    """Ask seeds.scad for its effective grid instead of duplicating its math."""
    cmd = [
        openscad,
        "--export-format", "echo",
        "-o", "-",
        "-D", f"bed=[{bed_w},{bed_h}]",
        "-D", f"columns={columns}",
        "-D", f"rows={rows}",
        str(scad),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"openscad failed reading the grid:\n{result.stderr}")

    matches = GRID_ECHO_RE.findall(result.stdout + "\n" + result.stderr)
    if len(matches) != 1:
        sys.exit("error: could not read exactly one grid echo from seeds.scad; "
                 "expected 'grid: C x R = ...'")
    return tuple(int(value) for value in matches[0])


def read_3mf_part(path):
    """Return a part's mesh and effective display color from an OpenSCAD 3MF."""
    with zipfile.ZipFile(path) as package:
        root = ET.fromstring(package.read("3D/3dmodel.model"))

    obj = root.find(f"./{{{CORE_NS}}}resources/{{{CORE_NS}}}object")
    if obj is None:
        raise ValueError(f"{path} contains no 3MF object")
    mesh = obj.find(f"{{{CORE_NS}}}mesh")
    if mesh is None:
        raise ValueError(f"{path} contains no 3MF mesh")

    material_index = obj.get("pindex", "0")
    triangles = mesh.findall(f".//{{{CORE_NS}}}triangle")
    triangle_materials = {triangle.get("p1") for triangle in triangles
                          if triangle.get("p1") is not None}
    if len(triangle_materials) == 1:
        material_index = triangle_materials.pop()
    for triangle in triangles:
        for attribute in ("pid", "p1", "p2", "p3"):
            triangle.attrib.pop(attribute, None)

    material_id = obj.get("pid")
    group = root.find(
        f"./{{{CORE_NS}}}resources/{{{CORE_NS}}}basematerials"
        f"[@id='{material_id}']"
    )
    if group is None:
        raise ValueError(f"{path} contains no matching base-material group")
    materials = group.findall(f"{{{CORE_NS}}}base")
    color = materials[int(material_index)].get("displaycolor")
    return deepcopy(mesh), color


def assemble_3mf(base_path, text_path, output_path, title):
    """Package aligned base/text meshes as components of one 3MF object."""
    base_mesh, base_color = read_3mf_part(base_path)
    text_mesh, text_color = read_3mf_part(text_path)

    model = ET.Element(f"{{{CORE_NS}}}model", {
        "unit": "millimeter",
        f"{{{XML_NS}}}lang": "en-US",
    })
    for name, value in (("Title", title),
                        ("Application", "SeedPills render_batches.py")):
        metadata = ET.SubElement(model, f"{{{CORE_NS}}}metadata", {"name": name})
        metadata.text = value

    resources = ET.SubElement(model, f"{{{CORE_NS}}}resources")
    materials = ET.SubElement(resources, f"{{{CORE_NS}}}basematerials",
                              {"id": "1"})
    ET.SubElement(materials, f"{{{CORE_NS}}}base",
                  {"name": "Base", "displaycolor": base_color})
    ET.SubElement(materials, f"{{{CORE_NS}}}base",
                  {"name": "Text", "displaycolor": text_color})

    for object_id, name, material_index, mesh in (
            ("2", "Base", "0", base_mesh),
            ("3", "Text", "1", text_mesh)):
        obj = ET.SubElement(resources, f"{{{CORE_NS}}}object", {
            "id": object_id,
            "name": name,
            "type": "model",
            "pid": "1",
            "pindex": material_index,
        })
        obj.append(mesh)

    assembly = ET.SubElement(resources, f"{{{CORE_NS}}}object", {
        "id": "4", "name": title, "type": "model",
    })
    components = ET.SubElement(assembly, f"{{{CORE_NS}}}components")
    ET.SubElement(components, f"{{{CORE_NS}}}component", {"objectid": "2"})
    ET.SubElement(components, f"{{{CORE_NS}}}component", {"objectid": "3"})
    build = ET.SubElement(model, f"{{{CORE_NS}}}build")
    ET.SubElement(build, f"{{{CORE_NS}}}item", {"objectid": "4"})

    with zipfile.ZipFile(base_path) as source:
        content_types = source.read("[Content_Types].xml")
        relationships = source.read("_rels/.rels")
    model_xml = ET.tostring(model, encoding="utf-8", xml_declaration=True)
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as package:
        package.writestr("[Content_Types].xml", content_types)
        package.writestr("_rels/.rels", relationships)
        package.writestr("3D/3dmodel.model", model_xml)


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
    if not all(math.isfinite(v) and v > 0 for v in (bed_w, bed_h)):
        sys.exit("error: --bed dimensions must be positive finite numbers")

    columns, rows = read_grid(openscad, args.scad, bed_w, bed_h,
                              args.columns, args.rows)
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
            "-D", f"plate_number={batch + 1}",
            "-D", f"plate_count={total_batches}",
            "-D", f"bed=[{bed_w},{bed_h}]",
            "-D", f"columns={columns}",
            "-D", f"rows={rows}",
            "-D", f"double_sided={'true' if args.double_sided else 'false'}",
        ]

        def render_part(part, out):
            cmd = [openscad, "-o", str(out), *defines,
                   "-D", f'render_part="{part}"', str(args.scad)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                sys.exit(f"openscad failed rendering {part}:\n{result.stderr}")

        if args.format == "3mf":
            with tempfile.TemporaryDirectory(prefix="seedpills-") as temp_dir:
                base = Path(temp_dir) / "base.3mf"
                text = Path(temp_dir) / "text.3mf"
                render_part("base", base)
                render_part("text", text)
                assemble_3mf(base, text, args.out / f"{stem}.3mf", stem)
        else:
            # STL has no multipart container, so retain two aligned files.
            for part in ("base", "text"):
                render_part(part, args.out / f"{stem}_{part}.stl")
    print("done")


if __name__ == "__main__":
    main()
