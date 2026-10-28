# MonoBEN: Monocular 3D Object Detection Beyond Fixed Camera iNtrinsics

Project page for **MonoBEN**, a unified intrinsic-aware monocular 3D detector that encodes
continuous, logarithmically normalized focal parameters through a lightweight numeric encoder,
with hierarchical conditioning at both the feature and query levels.

**Authors:** [Quoc Huy Nguyen](mailto:huy.nguyen2504@hcmut.edu.vn),
[Chi Dai Le](mailto:dai.lechi@hcmut.edu.vn), and
[Duc Dung Nguyen](mailto:nddung@hcmut.edu.vn) (\* corresponding author) —
AITech Lab., Faculty of Computer Science and Engineering,
Ho Chi Minh City University of Technology (HCMUT),
Vietnam National University Ho Chi Minh City.

## Project page

The page is implemented in [`index.html`](index.html) and deployed directly via GitHub Pages:

- Cross-Focal Performance at a Glance (850 px / 1400 px SVG chart)
- Abstract
- Overall Pipeline
- Generalization on Synthetic Intrinsics
- Standard KITTI Results
- Analytic

Accepted at **RIVF 2026**.

The vector tables are generated from `static/tabels/focal_gen.tex` and
`static/tabels/kitti_main_result.tex`. Desktop, tablet, and mobile versions use
15 px text; narrower versions stack column groups to avoid horizontal scrolling.
To regenerate the tables and chart (Python with matplotlib):

```sh
MPLCONFIGDIR=/tmp/monoben-matplotlib python static/tabels/render_assets.py
```

When changing table data, also update the accessible HTML tables in `index.html`.
