# SeedPills

Create your own set of 3D-printed BIP39 bitcoin lottery pieces!

Everything lives in `seeds.scad`, a single parametric OpenSCAD file
(https://openscad.org). No Python required for normal use.

## Quick start

1. Open `seeds.scad` in OpenSCAD.
2. Set `first`, `columns`, and `rows` in the parameter block at the top.
   Word indices are 0-based: `first = 0` starts at "abandon".
3. Preview (F5), Render (F6), then File > Export > Export as STL.

Each pill carries two words: word `first + i` on one face and word
`first + i + 1024` on the other, so a full set is 1024 two-sided pills.
The pills are interlocked with small breakaway links so they stay in order
on the build plate and can be verified before snapping apart.

## Printing on a Bambu P1S with a 0.2mm nozzle

The default dimensions are tuned so every small feature is an integer
number of extrusion lines or layers:

| Feature            | Size     | Why                                    |
|--------------------|----------|----------------------------------------|
| Pill height        | 3.00 mm  | 25 layers at 0.12 mm                   |
| Relief depth       | 0.48 mm  | 4 layers at 0.12 mm                    |
| Rim around relief  | 0.80 mm  | 2 perimeters at 0.2 mm nozzle          |
| Interlock links    | 0.44 mm  | 2 extrusion lines at 0.22 mm width     |

Recommended slicer settings (Bambu Studio / OrcaSlicer):

- Layer height: 0.12 mm (or 0.08/0.10/0.16 -- any divisor of 0.48 mm)
- Line width: 0.22-0.25 mm
- 3 walls so the lettering prints solid and crisp
- No supports needed; letters are recessed in a pocket, not bridging
- Slow down the first layers (the interlocks are tiny features)
- PLA or PETG both work; the links snap cleanly by hand or with a spatula

If you use a different layer height, set `deep` in `seeds.scad` to a
multiple of it (e.g. 0.5 for 0.1 mm layers).

The lettering font is [Fredoka](https://fonts.google.com/specimen/Fredoka)
(install it before rendering, or change the `font` variable).

## Batch rendering all 2048 words (optional)

`render_batches.py` drives the OpenSCAD CLI to render a full set of STL
batches in one go -- the only remaining use for Python here:

    python3 render_batches.py                       # 8 batches of 8x16 grids
    python3 render_batches.py --first 512 --count 1 # just one batch
    python3 render_batches.py --columns 5 --rows 5  # custom grid

A grid must hold a number of words that divides 2048 so batch boundaries
never split a word pair (the script checks this for you).
