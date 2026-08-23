# SeedPills

Create a printable set of 2,048 BIP39 word tiles for seed-phrase games,
demonstrations, and offline random selection.

![Close-up of two-color SeedPills with bold raised lettering](pictures/seedpills-closeup.png)

Each pill is a thin, standalone tile with bold raised text designed around a
0.4 mm nozzle. The first four letters identify every BIP39 English word
uniquely. Shorter words use all their letters.

> [!CAUTION]
> Treat a selected seed phrase like a password. Do not photograph it, upload
> it, or use an unverified selection process to secure real funds.

## Design highlights

- Separate base and text meshes for two-color printing
- Vendor-neutral STL output; no slicer-specific project format required
- Clean individual pills without breakaway-link scars
- 2.0 mm total thickness: 1.6 mm base plus 0.4 mm raised text
- Fredoka Bold lettering expanded by 0.12 mm for reliable 0.4 mm printing
- 0.4 mm gaps between pills—close together without shared geometry
- Dedicated 20 mm strip for an approximately 20 × 20 mm prime tower
- Automatic P1S/X1C bed layout with configurable dimensions

## Quick start

Requirements:

- [OpenSCAD](https://openscad.org/)
- [Fredoka](https://fonts.google.com/specimen/Fredoka), installed with the
  Bold style
- Python 3 only if you want to render batches automatically

To inspect or export directly:

1. Open `seeds.scad` in OpenSCAD.
2. Set `first` to the zero-based index of the first word (`0` starts with
   `ABAN`). Leave `columns = 0` and `rows = 0` to fill the configured bed.
3. Set `render_part` to `"base"` and export an STL.
4. Set `render_part` to `"text"` and export a second STL with the same grid
   settings.

For the complete word list, use the batch renderer:

```sh
python3 render_batches.py
```

This produces seven matching base/text pairs in `stl_files/`. Generated STL
and 3MF files are ignored by Git and are never intended to be committed.

## Two-color slicer workflow

For each plate, select the matching `_base.stl` and `_text.stl` files and
import them **at the same time**. When the slicer asks, load them as one object
with multiple parts. Do not auto-arrange the two parts separately; their shared
coordinates provide the alignment.

Then assign one filament or extruder to the base part and another to the text
part. This workflow works with Bambu Studio, OrcaSlicer, PrusaSlicer, and other
slicers that support multipart models.

Example pair:

```text
SeedPills_single_11x27_0001_0297_base.stl
SeedPills_single_11x27_0001_0297_text.stl
```

## Default plate layout

![Full SeedPills plate with the prime-tower keep-out highlighted](pictures/seedpills-plate.png)

The defaults target a 256 × 256 mm Bambu P1S/X1C build plate:

| Setting | Default | Purpose |
|---|---:|---|
| Grid | 11 × 27 | 297 pills on each full plate |
| Pill size | 18.5 × 7.5 mm | Compact, easy-to-handle tile |
| Pill gap | 0.4 mm | One nozzle width, with no shared geometry |
| Bed margin | 4 mm | Clearance for skirt or brim |
| Front-left exclusion | 18 × 28 mm | Cutter/wiper clearance |
| Prime-tower reserve | 20 mm wide | Clear strip at the right edge |

The complete 2,048-word single-sided set occupies seven plates. Unused slots
on the last plate are left blank.

The `prime_tower` setting is `[20, 20]`. The current rectangular grid reserves
its 20 mm width as a full-height strip, which is conservative and lets the
slicer place the tower anywhere along that edge.

## Print settings

Recommended starting point for PLA or PETG:

| Setting | Recommendation |
|---|---|
| Nozzle | 0.4 mm |
| Layer height | 0.2 mm |
| Line width | 0.45–0.5 mm |
| Walls | 3 |
| Supports | None |

The base is eight 0.2 mm layers and the text is two more layers. If adhesion
is marginal, use a small per-object brim. A shared brim can join neighboring
pills and leave rough edges.

## Batch-rendering options

```sh
python3 render_batches.py                     # all plates, paired STLs
python3 render_batches.py --first 297 --count 1
python3 render_batches.py --columns 8 --rows 16
python3 render_batches.py --bed 256,256
python3 render_batches.py --double-sided
python3 render_batches.py --format 3mf        # paired standard 3MF files
python3 render_batches.py --out another_folder
```

On macOS, the script finds the OpenSCAD application bundle automatically.
Elsewhere, put `openscad` on `PATH` or pass `--openscad /path/to/openscad`.

Output names follow this pattern:

```text
SeedPills_<sides>_<columns>x<rows>_<first>-<last>_<part>.<format>
```

## Useful parameters

Edit these near the top of `seeds.scad`:

| Parameter | Meaning |
|---|---|
| `first` | Zero-based first word index |
| `columns`, `rows` | Grid dimensions; `0` enables automatic sizing |
| `bed` | Build-plate width and depth in millimeters |
| `prime_tower` | Requested tower footprint in millimeters |
| `spacing` | Gap between neighboring pills |
| `render_part` | `"both"`, `"base"`, or `"text"` |
| `connected` | Add optional breakaway links |
| `double_sided` | Put the upper 1,024 words on the reverse side |
| `font`, `font_size` | Typeface and letter height |
| `text_weight` | Outward glyph expansion |

The source of truth is [seeds.scad](seeds.scad). `render_batches.py` is only
an automation helper; OpenSCAD remains sufficient for editing the model.
