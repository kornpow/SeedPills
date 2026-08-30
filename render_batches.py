#!/usr/bin/env python3
"""Render SeedPills print plates headlessly with the OpenSCAD CLI.

OpenSCAD alone is enough to design and export a grid interactively; this
script is only for automation: rendering a full set of plates covering all
2048 BIP39 words in one go. By default each plate auto-fills a 256x256mm
bed and exports paired STL files.

Usage:
    python3 render_batches.py                    # all plates, STL, auto grid
    python3 render_batches.py --open-bambu 5     # regenerate all, open P5/7
    python3 render_batches.py --double-sided     # 1024 pills instead of 2048
    python3 render_batches.py --format 3mf       # 3MF instead of STL
    python3 render_batches.py --first 324 --count 1

Requires an `openscad` binary; on macOS the OpenSCAD app bundle is
auto-detected (or pass --openscad /path/to/openscad).
"""

import argparse
import json
import math
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
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


def read_ascii_stl_xy_extents(path):
    """Return X/Y extents from an ASCII STL emitted by OpenSCAD."""
    xs, ys = [], []
    with path.open() as stl:
        for line in stl:
            fields = line.split()
            if len(fields) == 4 and fields[0] == "vertex":
                xs.append(float(fields[1]))
                ys.append(float(fields[2]))
    if not xs:
        raise ValueError(f"{path} contains no ASCII STL vertices")
    return max(xs) - min(xs), max(ys) - min(ys)


def validate_and_patch_bambu_project(project, base_stl, bed_size):
    """Make Bambu's temporary project deterministic, then validate it."""
    with zipfile.ZipFile(project) as source:
        members = {info.filename: source.read(info.filename)
                   for info in source.infolist()}

    settings_name = "Metadata/project_settings.config"
    model_settings_name = "Metadata/model_settings.config"
    model_name = "3D/3dmodel.model"
    settings = json.loads(members[settings_name])
    settings.update({
        "printable_area": [
            "0x0", f"{bed_size[0]}x0", f"{bed_size[0]}x{bed_size[1]}",
            f"0x{bed_size[1]}",
        ],
        "bed_exclude_area": ["0x0", "18x0", "18x28", "0x28"],
        "curr_bed_type": "Textured PEI Plate",
        "filament_colour": ["#000000", "#F97316"],
        "default_filament_colour": ["#000000", "#F97316"],
        "filament_settings_id": [
            "Bambu PLA Basic @BBL P1S 0.4 nozzle",
            "Bambu PLA Basic @BBL P1S 0.4 nozzle",
        ],
        "enable_prime_tower": "1",
        "prime_tower_width": "20",
        "wipe_tower_x": ["210"],
        "wipe_tower_y": ["4"],
        "wipe_tower_no_sparse_layers": "0",
    })
    members[settings_name] = (json.dumps(settings, indent=4) + "\n").encode()

    model_settings = ET.fromstring(members[model_settings_name])
    extruders = [node.get("value") for node in model_settings.findall(
        ".//metadata[@key='extruder']")]
    if extruders != ["1", "2"]:
        raise ValueError(f"Bambu part assignment is {extruders}, expected 1,2")

    model = ET.fromstring(members[model_name])
    item = model.find(f".//{{{CORE_NS}}}build/{{{CORE_NS}}}item")
    if item is None or not item.get("transform"):
        raise ValueError("Bambu project has no positioned build item")
    original_transform = item.get("transform")
    transform = [float(value) for value in original_transform.split()]
    object_model = ET.fromstring(members["3D/Objects/object_1.model"])
    object_z_bounds = {}
    for obj in object_model.findall(f".//{{{CORE_NS}}}object"):
        z_values = [float(vertex.get("z")) for vertex in obj.findall(
            f".//{{{CORE_NS}}}vertex")]
        if z_values:
            object_z_bounds[obj.get("id")] = (min(z_values), max(z_values))
    component_min_z = []
    for component in model.findall(f".//{{{CORE_NS}}}component"):
        component_transform = [float(value) for value in
                               component.get("transform").split()]
        mesh_min_z = object_z_bounds[component.get("objectid")][0]
        component_min_z.append(mesh_min_z + component_transform[11])
    if not component_min_z:
        raise ValueError("Bambu project has no mesh components")
    # Bambu's headless assembler emits a negative Y build translation even
    # though 3MF uses ordinary positive bed coordinates. Normalize it before
    # validating; otherwise the model opens completely below the plate.
    transform[10] = abs(transform[10])
    transform[11] = -min(component_min_z)
    updated_transform = " ".join(f"{value:.9g}" for value in transform)
    model_bytes = members[model_name]
    old_attribute = f'transform="{original_transform}"'.encode()
    new_attribute = f'transform="{updated_transform}"'.encode()
    if model_bytes.count(old_attribute) != 1:
        raise ValueError("could not uniquely locate Bambu build transform")
    members[model_name] = model_bytes.replace(old_attribute, new_attribute)
    final_min_z = min(component_min_z) + transform[11]
    if abs(final_min_z) > 1e-6:
        raise ValueError(f"model minimum Z is {final_min_z}, expected 0")

    center_x, center_y = transform[9], transform[10]
    extent_x, extent_y = read_ascii_stl_xy_extents(base_stl)
    model_bounds = (center_x - extent_x / 2, center_y - extent_y / 2,
                    center_x + extent_x / 2, center_y + extent_y / 2)
    tower_bounds = (210, 4, 230, 24)
    exclusion_bounds = (0, 0, 18, 28)

    def intersects(a, b):
        return a[0] < b[2] and a[2] > b[0] \
            and a[1] < b[3] and a[3] > b[1]

    tolerance = 0.01  # Bambu transforms commonly contain ~1e-5 mm roundoff.
    if (model_bounds[0] < -tolerance or model_bounds[1] < -tolerance
            or model_bounds[2] > bed_size[0] + tolerance
            or model_bounds[3] > bed_size[1] + tolerance):
        raise ValueError(f"model is outside the bed: {model_bounds}")
    if intersects(model_bounds, exclusion_bounds):
        raise ValueError(f"model intersects exclusion zone: {model_bounds}")
    if intersects(model_bounds, tower_bounds):
        raise ValueError(f"model intersects prime tower: {model_bounds}")

    validated = project.with_name(project.stem + "-validated.3mf")
    with zipfile.ZipFile(validated, "w", zipfile.ZIP_DEFLATED) as output:
        for name, data in members.items():
            output.writestr(name, data)
    validated.replace(project)
    return model_bounds, tower_bounds, transform[11]


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
    p.add_argument("--open-bambu", type=int, metavar="PLATE",
                   help="render every plate to a temporary folder, then open "
                        "this 1-based plate in Bambu Studio with the repo preset")
    args = p.parse_args()

    if args.open_bambu is not None:
        if platform.system() != "Darwin":
            sys.exit("error: --open-bambu currently requires macOS")
        if args.first != 0 or args.count != 0:
            sys.exit("error: --open-bambu always regenerates all plates; "
                     "do not combine it with --first or --count")
        if args.format != "stl":
            sys.exit("error: --open-bambu uses the vendor-neutral STL pair")
        args.out = Path(tempfile.mkdtemp(prefix="seedpills-bambu-"))

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
    if args.open_bambu is not None \
            and not 1 <= args.open_bambu <= total_batches:
        sys.exit(f"error: --open-bambu plate must be 1..{total_batches}")
    start_batch = args.first // per_batch
    stop = total_batches if args.count == 0 else start_batch + args.count

    sides = "double" if args.double_sided else "single"
    print(f"grid: {columns}x{rows} = {columns * rows} pills/plate, "
          f"{total_batches} plates for {WORDS_TOTAL} words", flush=True)
    args.out.mkdir(exist_ok=True)
    rendered_stems = {}
    for batch in range(start_batch, stop):
        first = batch * per_batch
        last = min(first + per_batch, WORDS_TOTAL)
        stem = (f"SeedPills_{sides}_{columns}x{rows}_"
                f"{first + 1:04d}_{last:04d}")
        rendered_stems[batch + 1] = stem
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

    if args.open_bambu is not None:
        preset = Path(__file__).with_name("presets") \
            / "SeedPills 0.20mm @BBL P1S.json"
        machine = Path(
            "/Applications/BambuStudio.app/Contents/Resources/profiles/BBL/"
            "machine/Bambu Lab P1S 0.4 nozzle.json"
        )
        filament = Path(
            "/Applications/BambuStudio.app/Contents/Resources/profiles/BBL/"
            "filament/Bambu PLA Basic @BBL P1S 0.4 nozzle.json"
        )
        for required in (machine, filament):
            if not required.exists():
                sys.exit(f"error: Bambu profile not found: {required}")
        stem = rendered_stems[args.open_bambu]
        base = (args.out / f"{stem}_base.stl").resolve()
        text = (args.out / f"{stem}_text.stl").resolve()
        project = args.out / f"{stem}-Bambu.3mf"
        bambu = "/Applications/BambuStudio.app/Contents/MacOS/BambuStudio"
        export = subprocess.run([
            bambu,
            "--load-settings", f"{preset.resolve()};{machine}",
            "--load-filaments", f"{filament};{filament}",
            "--load-filament-ids", "1,2",
            "--allow-multicolor-oneplate",
            "--assemble", "--arrange", "1",
            "--export-3mf", str(project),
            str(base), str(text),
        ], cwd=args.out, capture_output=True, text=True)
        if export.returncode != 0 or not project.exists():
            sys.exit("Bambu project export failed:\n"
                     + export.stdout + export.stderr)

        model_bounds, tower_bounds, z_offset = validate_and_patch_bambu_project(
            project, base, (bed_w, bed_h))
        print(f"validated P{args.open_bambu}/{total_batches}: "
              f"base=filament 1 black, text=filament 2 orange")
        print(f"model bounds: {tuple(round(v, 2) for v in model_bounds)}")
        print(f"tower bounds: {tower_bounds}")
        print(f"build Z offset: {z_offset:.2f} mm (minimum Z = 0)")
        # Bambu's CLI exporter leaves a GUI process behind. Close it so the
        # validated project cannot be hidden behind a stale import window.
        subprocess.run([
            "osascript", "-e", 'tell application "BambuStudio" to quit',
        ], capture_output=True)
        for _ in range(40):
            if subprocess.run(["pgrep", "-f", bambu],
                              capture_output=True).returncode != 0:
                break
            time.sleep(0.25)
        else:
            sys.exit("error: stale Bambu Studio process did not quit")
        subprocess.Popen(
            ["open", "-na", "BambuStudio", str(project)],
            cwd=args.out,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )


if __name__ == "__main__":
    main()
