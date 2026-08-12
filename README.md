# SeedPills

Create your own set of 3D-printed BIP39 bitcoin lottery pieces!

Everything lives in `seeds.scad`, a single parametric OpenSCAD file
(https://openscad.org). No Python required for normal use.

## Quick start

1. Open `seeds.scad` in OpenSCAD.
2. Set `first` to the 0-based index of the first word (`0` = "abandon").
   Leave `columns = 0` and `rows = 0` to auto-fill the bed, or set them
   explicitly.
3. Preview (F5), Render (F6), then File > Export > Export as STL.

By default each pill is **single-sided** (one word, printed flat with no
flipping). The pills are interlocked with small breakaway links so they stay
in order on the build plate and can be verified before snapping apart.

Set `double_sided = true` to put word `i + 1024` on the back face of each
pill -- that halves the pill count (1024 pills for the full list) but needs a
two-sided print. Single-sided needs 2048 pills for the full 2048-word list.

## Printing on a Bambu P1S with a 0.4mm nozzle

The default dimensions are tuned so every small feature is an integer number
of extrusion lines or layers:

| Feature            | Size     | Why                                |
|--------------------|----------|------------------------------------|
| Pill height        | 3.00 mm  | 15 layers at 0.2 mm                |
| Relief depth       | 0.60 mm  | 3 layers at 0.2 mm                 |
| Rim around relief  | 0.90 mm  | 2 perimeters at 0.45 mm line width |
| Interlock links    | 0.50 mm  | 1 extrusion line, snaps by hand    |

Recommended slicer settings (Bambu Studio / OrcaSlicer):

- Nozzle: 0.4 mm, layer height 0.2 mm (any divisor of 0.6 mm works)
- Line width: 0.45-0.5 mm
- 3 walls so the lettering prints solid and crisp
- No supports needed; letters are recessed in a pocket, not bridging
- PLA or PETG both work; the links snap cleanly by hand or with a spatula

If you use a different layer height, set `deep` in `seeds.scad` to a multiple
of it (e.g. 0.48 for 0.12 mm layers).

The lettering font is [Fredoka](https://fonts.google.com/specimen/Fredoka)
(install it before rendering, or change the `font` variable).

## Maximizing the print bed

With `columns = 0` and `rows = 0`, the grid auto-fills the `bed` size
(default `[256, 256]` for the P1S/X1C). At the default pill size that is a
13x32 plate = 416 pills. The full 2048-word list takes 5 plates; the last
plate simply leaves its unused slots blank.

## Batch rendering the full word list (optional)

`render_batches.py` drives the OpenSCAD CLI to render every plate in one go:

    python3 render_batches.py                    # all plates, auto grid
    python3 render_batches.py --double-sided     # 1024 pills instead of 2048
    python3 render_batches.py --columns 8 --rows 16
    python3 render_batches.py --bed 256,256      # custom bed size
    python3 render_batches.py --first 416 --count 1
    python3 render_batches.py --format stl       # STL instead of 3MF

Output defaults to **3MF**, which is zip-compressed (~6 MB/plate vs ~113 MB
for the same mesh as STL) and loads far more smoothly in Bambu Studio. Use
`--format stl` only if your slicer needs it.

On macOS it auto-detects the OpenSCAD app bundle if `openscad` is not on
PATH. Plates are named `SeedPills_<sides>_<cols>x<rows>_<first>-<last>.<fmt>`.
