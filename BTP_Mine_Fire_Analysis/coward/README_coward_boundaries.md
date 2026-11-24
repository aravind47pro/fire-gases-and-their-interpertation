# Coward Diagram Boundaries Reference and Configuration Guide

## Purpose
This directory contains boundary coordinate definitions for the Coward Explosibility Diagram (Methane vs Oxygen in Nitrogen-diluted mine atmospheres).

According to academic requirements for this BTP project:
- **No boundary coordinates are invented or fabricated.**
- Two files are provided:
  1. `coward_boundaries.csv`: Populated with published classical coordinates from USBM Bulletin 503 (Coward & Jones, 1952) and USBM Bulletin 627 (Zabetakis, 1965).
  2. `coward_boundaries_template.csv`: A blank configurable template to be filled if a specific custom reference (e.g., from your supervisor or specific Indian coal mine literature) is provided.

## Published Reference Coordinates (USBM Bulletin 503 / 627)
- **Air Line (Dilution Line)**: Connects (0% CH₄, 20.93% O₂) to (100% CH₄, 0% O₂). Equation: \(O_2 = 20.93 \times (1 - \frac{CH_4}{100})\).
- **Lower Explosive Limit (LEL) in normal air**: 5.0% CH₄, 19.88% O₂.
- **Upper Explosive Limit (UEL) in normal air**: 15.0% CH₄, 17.79% O₂.
- **Nose Limit (Minimum Oxygen for flame propagation with N₂ diluent)**: 5.9% CH₄, 12.1% O₂.
- **Ray through Nose from Origin**: Slope = \(12.1 / 5.9 \approx 2.0508\). Intersects air line at approx. 14.28% CH₄, 17.94% O₂.

## Definition of Coward Zones
- **Zone A (Explosive Mixtures)**: Mixtures that propagate flame without addition of further air or methane.
- **Zone B (Capable of forming explosive mixtures with air)**: Methane-rich mixtures that, upon dilution with fresh air, pass through the explosive Zone A.
- **Zone C (Capable of forming explosive mixtures with methane)**: Oxygen-rich mixtures that become explosive if methane is added.
- **Zone D (Non-explosive / Cannot form explosive mixtures with air alone)**: Low oxygen or low fuel atmospheres that cannot form explosive mixtures when diluted with air alone (any air dilution ray stays entirely below/outside Zone A).
- **Zone E (Impossible Mixtures)**: Mixtures having oxygen concentrations exceeding normal atmospheric air dilution (\(O_2 > 20.93 \times (1 - CH_4/100)\)).

## Academic Note
If using the template or unverified boundaries, the software flags:
`Coward zone boundaries pending verification from the selected reference.`
When verified boundaries are loaded from `coward_boundaries.csv`, the source is explicitly cited on all plots, tables, and reports.
