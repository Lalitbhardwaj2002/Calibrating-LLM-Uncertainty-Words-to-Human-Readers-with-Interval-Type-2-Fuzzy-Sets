"""Fig. 1: flowchart of the ReadCal methodology in classic flowchart notation (terminators, processes, data, decision).
usage (from the repository root): python -m readcal.flowchart
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle

FS = 7.4                       # text size (pt)
LINE = 2.15                    # height of one text line in axis units
GAP = 2.6                      # arrow length between stacked symbols
plt.rcParams.update({"font.family": "Times New Roman", "mathtext.fontset": "stix", "font.size": FS})
INK, LANE, HEAD, EDGE = "#111111", "#F3F3F3", "#DCDCDC", "#9A9A9A"
H_UNITS = 107
fig, ax = plt.subplots(figsize=(6.3, H_UNITS * 0.0612), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, H_UNITS)
ax.axis("off")


def height(text, extra=0.0):
    return LINE * (text.count("\n") + 1) + 2.0 + extra


def label(x, y, tag):
    ax.text(x, y, tag, ha="right", va="center", fontsize=6.8, color="#444444", fontweight="bold")


def process(cx, top, w, text, tag=None, extra=0.0):
    h = height(text, extra)
    ax.add_patch(Rectangle((cx - w / 2, top - h), w, h, facecolor="white", edgecolor=INK, lw=0.8))
    ax.text(cx, top - h / 2, text, ha="center", va="center", fontsize=FS, color=INK, linespacing=1.3)
    if tag:
        label(cx - w / 2 - 0.7, top - h / 2, tag)
    return top - h


def terminator(cx, top, w, text):
    h = 4.6
    ax.add_patch(FancyBboxPatch((cx - w / 2, top - h), w, h, boxstyle=f"round,pad=0,rounding_size={h / 2}",
                                facecolor="white", edgecolor=INK, lw=1.0))
    ax.text(cx, top - h / 2, text, ha="center", va="center", fontsize=FS + 0.4, color=INK, fontweight="bold")
    return top - h


def data(cx, top, w, text, tag=None):
    h, s = height(text), 2.0
    pts = [(cx - w / 2 + s, top), (cx + w / 2 + s, top), (cx + w / 2 - s, top - h), (cx - w / 2 - s, top - h)]
    ax.add_patch(Polygon(pts, closed=True, facecolor="white", edgecolor=INK, lw=0.8))
    ax.text(cx, top - h / 2, text, ha="center", va="center", fontsize=FS, color=INK, linespacing=1.3)
    if tag:
        label(cx - w / 2 - s - 0.5, top - h / 2, tag)
    return top - h


def decision(cx, top, w, h, text):
    pts = [(cx, top), (cx + w / 2, top - h / 2), (cx, top - h), (cx - w / 2, top - h / 2)]
    ax.add_patch(Polygon(pts, closed=True, facecolor="white", edgecolor=INK, lw=0.8))
    ax.text(cx, top - h / 2, text, ha="center", va="center", fontsize=FS, color=INK)
    return top - h


def arrow(points, text=None, at=None):
    xs, ys = zip(*points)
    ax.plot(xs, ys, color=INK, lw=0.8, solid_capstyle="butt")
    ax.annotate("", xy=points[-1], xytext=points[-2],
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.8, mutation_scale=7, shrinkA=0, shrinkB=0))
    if text:
        ax.text(*at, text, fontsize=FS, color=INK, ha="center", va="center", fontstyle="italic")


def lane(x0, y0, w, h, title, tx=None, ha="left"):
    ax.add_patch(Rectangle((x0, y0), w, h, facecolor=LANE, edgecolor=EDGE, lw=0.6))
    ax.add_patch(Rectangle((x0, y0 + h - 4.2), w, 4.2, facecolor=HEAD, edgecolor=EDGE, lw=0.6))
    ax.text(x0 + 1.6 if tx is None else tx, y0 + h - 2.1, title, ha=ha, va="center", fontsize=FS + 0.8,
            fontweight="bold", color=INK)


# panels -----------------------------------------------------------------------------------------------------------
LC_TOP = 30.0
TOP_AB, BOT_AB = H_UNITS - 0.5, LC_TOP + 2.0
lane(0.5, BOT_AB, 49.0, TOP_AB - BOT_AB, "Claim reliability (fuzzy rule engine)")
lane(50.5, BOT_AB, 49.0, TOP_AB - BOT_AB, "Reader model (type-2 encoder, built once)")
lane(0.5, 0.5, 99.0, LC_TOP - 0.5, "Hedge selection (type-2 decoder)", tx=50, ha="center")

# claim reliability: from the prompt to a calibrated reliability -----------------------------------------------------------------
AX, AW = 27.5, 40.0
y = TOP_AB - 6.0
y = terminator(AX, y, 26, "Start: user prompt")
steps_a = [
    ("LLM writes the answer and draws\n20 further answers to the same prompt"),
    ("Split the answer into claims (sentences)"),
    ("Self-consistency of claim $i$:\n$x_E$ = lowest share of samples containing\na name or number of the claim\n"
           "$x_S$ = mean share of samples containing\nthe content words of the answer"),
    ("Fuzzify $x_E$ and $x_S$ into low, medium, high\n(triangular sets peaking at the\n10th, 50th and 90th percentiles)"),
    ("Fire the nine rules (product of memberships)\nand combine them on log-odds scale, Eq. (4)"),
    ("Isotonic calibration gives reliability $p_i$;\nthe strongest rule gives the rationale"),
]
for text in steps_a:
    arrow([(AX, y), (AX, y - GAP)])
    y = process(AX, y - GAP, AW, text, extra=0.6 if "$" in text else 0.0)
bottom_a = y

# reader model: from survey answers to type-2 fuzzy sets ---------------------------------------------------------------
BX, BW = 76.0, 40.0
y = TOP_AB - 6.0
y = data(BX, y, BW - 4, "Survey data: 165 readers give\na probability for each of 15 phrases")
steps_b = [
    ("Split the readers into three groups\n(online sample, students, graduates)"),
    ("For each group $g$ and phrase $h$: membership\nfunction $\mu_{g,h}$ from a kernel estimate, Eq. (5)"),
    ("Footprint of uncertainty of phrase $h$:\nenvelope of the three group sets, Eq. (6)"),
    ("Centroid $c_{g,h}$ (typical reading) and\nspread $s^2_{g,h}$ (disagreement), Eq. (7)"),
    ("Choose the vocabulary: the $k$ phrases\nwith the lowest worst-case loss (greedy)"),
]
for text in steps_b:
    arrow([(BX, y), (BX, y - GAP)])
    y = process(BX, y - GAP, BW, text, extra=0.6 if "$" in text else 0.0)
bottom_b = y

# hedge selection: decoding every claim -----------------------------------------------------------------------------------
CX, CW = 52.0, 88.0
c1_top = LC_TOP - 4.2 - 3.6
y_join = LC_TOP - 4.2 - 1.6
arrow([(AX, bottom_a), (AX, y_join), (40, y_join), (40, c1_top)])
arrow([(BX, bottom_b), (BX, y_join), (64, y_join), (64, c1_top)])
c1_text = ("For claim $i$ and every phrase $h$ in the vocabulary, take the worst reader group:\n"
           r"$L_i(h) = \max_g\,[(c_{g,h} - p_i)^2 + s^2_{g,h}]$, Eq. (9)")
c1_bot = process(CX, c1_top, CW, c1_text, extra=1.4)
row = c1_bot - 3.4 - 4.0
c2_text = r"Choose $h_i^* = \arg\min_h L_i(h)$" + "\nand attach the rule-based rationale"
c2_h = height(c2_text, 1.2)
arrow([(27.5, c1_bot), (27.5, row + c2_h / 2)])
process(27.5, row + c2_h / 2, 40, c2_text, extra=1.2)
DX = 61.5
arrow([(47.5, row), (DX - 10, row)])
decision(DX, row + 4.0, 20, 8.0, "More claims?")
arrow([(DX, row + 4.0), (DX, c1_bot)], "yes: next claim", (DX + 9.0, (row + 4.0 + c1_bot) / 2))
arrow([(DX + 10, row), (77.5, row)], "no", (74.0, row + 1.6))
terminator(88.0, row + 2.3, 21, "End: hedged answer")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(os.environ.get("READCAL_RESULTS", os.path.join(ROOT, "results")), "figures")
os.makedirs(OUT, exist_ok=True)
fig.savefig(os.path.join(OUT, "fig1_flowchart.png"), bbox_inches="tight", pad_inches=0.02)
print("written", os.path.join(OUT, "fig1_flowchart.png"))
