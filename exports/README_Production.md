# Chibees vector engineering pack

Rebuild: `python3 build_chibees_vectors.py` from the project root.

The 6 SVG editions contain only outlined path artwork. Master: 82 paths, 741 anchor commands, 369 cubic segments, 7 layers. Anchor count is M + L + C endpoints, including repeated closure endpoints; it is not a claim about Illustrator's UI node count.

## Color
- Fiesta red: #E22B24 / CMYK 0,92,95,0. Suggested Pantone 485 C or 1795 C; approve a physical swatch.
- Green: #198C38 / CMYK 84,0,85,23.
- Yellow: #F6C518 / CMYK 0,20,95,0.
- Espresso: #231915 / CMYK 40,50,50,90.
- Amber: #E58E1A / CMYK 0,43,89,10.

## Production scope
- Master .ai is a valid PDF 1.7 file with 7 optional-content layers, DeviceCMYK paths and XMP metadata. Opens through PDF-compatible import; not proprietary native AI editing data. Adobe Illustrator import/layer retention has not been interactively tested.
- EPS is PostScript Level 3 with process CMYK operators and no font/image references.
- 4-page PDF is a vector specification book in DeviceCMYK. No supplied printer ICC profile, OutputIntent or PDF/X certification; press acceptance requires printer proof. SVG effects are display treatments, not lighting construction plans.
- The DXF is R2010 / AC1024 in mm: height 1270.00, width 2228.07, inferred from the reconstructed silhouette. All entities are closed LWPOLYLINE; cubic curves are adaptively flattened to 0.02 mm chord tolerance. CUT_CABINET is the exterior cut; VINYL_* are color artwork boundaries; DETAIL_ENGRAVE contains decoration. Color shapes overlap intentionally; CAM operator must select/boolean the desired plates, set tool/kerf/depth, and omit small detail where unsuitable.
- White keyline is visible white artwork. Transparent PNG includes white artwork and a fully transparent background. On kraft media it needs white ink or a white vinyl substrate.
- PNG dimensions: 4000 x 3000 and 2400 x 1800; 300 DPI metadata.

## Source fidelity
Reconstruction from `ref/sign_crop_1to1.png`. The source is a photo of a display with moire and a cursor over the second e. Both e glyphs are exact translations of the same clean Bezier source (+85,+11 design units). Cabinet is symmetric; splash order is red/green/yellow on both sides. Micro-detail hidden by blur is reconstructed, not claimed as measured. 50-inch cabinet height follows the supplied brief and must be field-confirmed.

No platform submission or publication is performed by this generator.
