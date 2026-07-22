"""docs-html — dataviz: verify the chart colour tokens actually hold up.

`js/modules/charts.js` owns the design system's chart colours and its comments
claim they are "validated": colourblind-safe, legible on the chart surface.
This module is what makes that claim checkable instead of aspirational. Run it
with `python builder.py dataviz` after touching any colour there.

It reads the tokens straight out of charts.js — that file stays the single
source of truth, and a colour can never be validated here while differing there.

What it checks
--------------
1. CONTRAST of every categorical slot against the chart surface (#f7f9fb).
   Below 3:1 is not a failure: the documented *relief rule* already says such
   slots need data labels or a table view, so this reports them as needing
   relief and expects the author to comply.
2. PAIRWISE SEPARATION of the categorical palette under normal vision plus
   protanopia, deuteranopia and tritanopia. Two series that collapse into the
   same colour for ~8% of men is a real defect, so this DOES fail.
3. SEMANTIC tokens (positive/negative/caution) for contrast only. Their
   separation is reported but never fails — red/green confusion under
   deuteranopia is inherent to what those colours mean, which is precisely why
   charts.js requires a second, non-colour cue wherever they are used.
4. The sequential RAMP for monotonic luminance, which is what makes ordered
   data survive greyscale printing and every CVD. Non-monotonic fails.

Colour science: sRGB -> linear -> CIEXYZ -> CIELAB, distances in CIEDE2000
(the perceptual standard; CIE76 badly overstates differences in blues, which
is most of this palette). CVD simulation uses the Machado, Oliveira & Gomes
(2009) severity-1.0 matrices applied in linear RGB.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

CHARTS_JS = Path(__file__).resolve().parent / "js" / "modules" / "charts.js"

# The surface charts are drawn on (.chart-figure = --bg-soft), not page white.
SURFACE = "#f7f9fb"

# A categorical slot below this needs the relief rule (labels / table view).
RELIEF_CONTRAST = 3.0
# Below this CIEDE2000, two large colour areas read as "the same colour".
# Calibrated against the Okabe-Ito palette — the published reference for
# colourblind-safe categorical colour — which scores a worst pair of 11.1 across
# all eight slots under every CVD type simulated here. No eight-colour
# categorical set does meaningfully better, so a floor above ~11 would fail the
# state of the art and is not a standard anyone can meet. 10.0 sits just under
# it: strict enough that genuinely confusable pairs fail, loose enough that a
# correct palette passes.
MIN_SEPARATION = 10.0

# Machado et al. (2009), severity 1.0, applied to LINEAR rgb.
CVD = {
    "protanopia": ((0.152286, 1.052583, -0.204868),
                   (0.114503, 0.786281, 0.099216),
                   (-0.003882, -0.048116, 1.051998)),
    "deuteranopia": ((0.367322, 0.860646, -0.227968),
                     (0.280085, 0.672501, 0.047413),
                     (-0.011820, 0.042940, 0.968881)),
    "tritanopia": ((1.255528, -0.076749, -0.178779),
                   (-0.078411, 0.930809, 0.147602),
                   (0.004733, 0.691367, 0.303900)),
}


# --------------------------------------------------------------------------
# colour conversions
# --------------------------------------------------------------------------


def _hex_to_rgb(value: str) -> tuple[float, float, float]:
    v = value.lstrip("#")
    return tuple(int(v[i:i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def _to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _to_srgb(c: float) -> float:
    c = min(max(c, 0.0), 1.0)
    return c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def _luminance(value: str) -> float:
    """WCAG relative luminance."""
    r, g, b = (_to_linear(c) for c in _hex_to_rgb(value))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    """WCAG contrast ratio, 1.0 (identical) to 21.0 (black on white)."""
    la, lb = _luminance(a), _luminance(b)
    lo, hi = sorted((la, lb))
    return (hi + 0.05) / (lo + 0.05)


def simulate(value: str, kind: str) -> str:
    """The colour as seen with one form of dichromacy."""
    m = CVD[kind]
    lin = [_to_linear(c) for c in _hex_to_rgb(value)]
    out = [sum(m[row][col] * lin[col] for col in range(3)) for row in range(3)]
    return "#" + "".join(f"{round(_to_srgb(c) * 255):02x}" for c in out)


def _to_lab(value: str) -> tuple[float, float, float]:
    r, g, b = (_to_linear(c) for c in _hex_to_rgb(value))
    x = (0.4124564 * r + 0.3575761 * g + 0.1804375 * b) / 0.95047
    y = (0.2126729 * r + 0.7151522 * g + 0.0721750 * b) / 1.00000
    z = (0.0193339 * r + 0.1191920 * g + 0.9503041 * b) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 216 / 24389 else (24389 / 27 * t + 16) / 116
    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def delta_e(a: str, b: str) -> float:
    """CIEDE2000 perceptual distance."""
    l1, a1, b1 = _to_lab(a)
    l2, a2, b2 = _to_lab(b)
    avg_l = (l1 + l2) / 2
    c1, c2 = math.hypot(a1, b1), math.hypot(a2, b2)
    avg_c = (c1 + c2) / 2
    g = 0.5 * (1 - math.sqrt(avg_c ** 7 / (avg_c ** 7 + 25 ** 7))) if avg_c else 0.5
    a1p, a2p = a1 * (1 + g), a2 * (1 + g)
    c1p, c2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    avg_cp = (c1p + c2p) / 2
    h1p = math.degrees(math.atan2(b1, a1p)) % 360
    h2p = math.degrees(math.atan2(b2, a2p)) % 360

    if c1p * c2p == 0:
        dhp = 0.0
    elif abs(h2p - h1p) <= 180:
        dhp = h2p - h1p
    else:
        dhp = h2p - h1p - 360 if h2p > h1p else h2p - h1p + 360

    dlp, dcp = l2 - l1, c2p - c1p
    dhp_term = 2 * math.sqrt(c1p * c2p) * math.sin(math.radians(dhp) / 2)

    if c1p * c2p == 0:
        avg_hp = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        avg_hp = (h1p + h2p) / 2
    elif h1p + h2p < 360:
        avg_hp = (h1p + h2p + 360) / 2
    else:
        avg_hp = (h1p + h2p - 360) / 2

    t = (1 - 0.17 * math.cos(math.radians(avg_hp - 30))
         + 0.24 * math.cos(math.radians(2 * avg_hp))
         + 0.32 * math.cos(math.radians(3 * avg_hp + 6))
         - 0.20 * math.cos(math.radians(4 * avg_hp - 63)))
    sl = 1 + (0.015 * (avg_l - 50) ** 2) / math.sqrt(20 + (avg_l - 50) ** 2)
    sc = 1 + 0.045 * avg_cp
    sh = 1 + 0.015 * avg_cp * t
    rt = (-2 * math.sqrt(avg_cp ** 7 / (avg_cp ** 7 + 25 ** 7))
          * math.sin(math.radians(60 * math.exp(-(((avg_hp - 275) / 25) ** 2)))))
    return math.sqrt((dlp / sl) ** 2 + (dcp / sc) ** 2 + (dhp_term / sh) ** 2
                     + rt * (dcp / sc) * (dhp_term / sh))


# --------------------------------------------------------------------------
# reading the tokens out of charts.js
# --------------------------------------------------------------------------

HEX = re.compile(r'"(#[0-9a-fA-F]{6})"')


def _array(source: str, name: str) -> list[str]:
    m = re.search(rf"const {name} = \[(.*?)\];", source, re.S)
    if not m:
        raise SystemExit(f"dataviz: could not find {name} in {CHARTS_JS}")
    return HEX.findall(m.group(1))


def _semantic_tokens(source: str) -> dict[str, str]:
    m = re.search(r"const TOKENS = \{(.*?)\n  \};", source, re.S)
    if not m:
        raise SystemExit(f"dataviz: could not find TOKENS in {CHARTS_JS}")
    pairs = re.findall(r"(\w+):\s*\"(#[0-9a-fA-F]{6})\"", m.group(1))
    return {k: v for k, v in pairs if k in ("positive", "negative", "caution")}


# --------------------------------------------------------------------------
# the check
# --------------------------------------------------------------------------


def check() -> int:
    """Print the report; return a process exit code (0 = every rule holds)."""
    source = CHARTS_JS.read_text(encoding="utf-8")
    palette = _array(source, "PALETTE")
    ramp = _array(source, "RAMP")
    semantic = _semantic_tokens(source)
    failures: list[str] = []

    print(f"dataviz — {CHARTS_JS.relative_to(CHARTS_JS.parents[2])}"
          f"  (surface {SURFACE})\n")

    # 1. categorical contrast -------------------------------------------------
    print(f"categorical palette — contrast vs surface (relief below {RELIEF_CONTRAST}:1)")
    relief = []
    # Slots are numbered from 1, matching how the authoring rules refer to them
    # ("slots 3-5 sit below 3:1" in chart-apache-echarts/usage.md).
    for i, colour in enumerate(palette, start=1):
        ratio = contrast(colour, SURFACE)
        flag = "" if ratio >= RELIEF_CONTRAST else "  <- needs relief"
        if flag:
            relief.append(i)
        print(f"  slot {i}  {colour}  {ratio:5.2f}:1{flag}")
    if relief:
        print(f"  slots {relief} require data labels or a table view "
              f"(documented relief rule, not a failure)")

    # 2. categorical separation ----------------------------------------------
    print(f"\ncategorical palette — pairwise separation "
          f"(CIEDE2000, floor {MIN_SEPARATION})")
    for vision in ("normal", *CVD):
        seen = (palette if vision == "normal"
                else [simulate(c, vision) for c in palette])
        worst, pair = math.inf, None
        for i in range(len(seen)):
            for j in range(i + 1, len(seen)):
                d = delta_e(seen[i], seen[j])
                if d < worst:
                    worst, pair = d, (i + 1, j + 1)      # slots count from 1
        ok = worst >= MIN_SEPARATION
        print(f"  {vision:<13} worst pair {pair}  dE {worst:5.1f}"
              f"  {'ok' if ok else 'FAIL'}")
        if not ok:
            failures.append(f"palette slots {pair[0]} and {pair[1]} are "
                            f"indistinguishable under {vision} (dE {worst:.1f})")

    # 3. semantic tokens ------------------------------------------------------
    print("\nsemantic direction tokens — contrast only; separation informational")
    for name, colour in semantic.items():
        print(f"  {name:<9} {colour}  {contrast(colour, SURFACE):5.2f}:1")
    if "positive" in semantic and "negative" in semantic:
        d = delta_e(simulate(semantic["positive"], "deuteranopia"),
                    simulate(semantic["negative"], "deuteranopia"))
        print(f"  positive vs negative under deuteranopia: dE {d:.1f} — "
              f"{'expected collapse' if d < MIN_SEPARATION else 'separable'}; "
              f"never encode direction by colour alone")

    # 4. sequential ramp ------------------------------------------------------
    print("\nsequential ramp — luminance must be monotonic")
    lums = [_luminance(c) for c in ramp]
    monotonic = all(x > y for x, y in zip(lums, lums[1:]))
    for colour, lum in zip(ramp, lums):
        print(f"  {colour}  L {lum:.3f}")
    print(f"  {'monotonic ok' if monotonic else 'FAIL — not monotonic'}")
    if not monotonic:
        failures.append("RAMP luminance is not monotonic; it will not survive "
                        "greyscale print or CVD")

    # verdict -----------------------------------------------------------------
    print()
    if failures:
        for f in failures:
            print(f"FAIL: {f}")
        return 1
    print("all dataviz rules hold")
    return 0
