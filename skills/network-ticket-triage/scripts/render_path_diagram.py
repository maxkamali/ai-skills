#!/usr/bin/env python3
"""Render pair-separated directional network-ticket triage diagrams."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

WHITE = "#FFFFFF"
BLACK = "#202124"
DARK = "#4F5963"
GREY = "#8A949E"
GRID = "#E5E9ED"
PALE = "#F7F8FA"
BLUE = "#1565C0"
RED = "#C62828"
GREEN = "#2E7D32"
AMBER = "#A96300"
COLORS = {
    "reported": BLUE,
    "impaired": RED,
    "healthy": GREEN,
    "not_provided": GREY,
    "inconclusive": AMBER,
    "neutral": DARK,
}
LABELS = {
    "reported": "REPORTED",
    "impaired": "IMPAIRED",
    "healthy": "WORKING",
    "not_provided": "NOT PROVIDED",
    "inconclusive": "INCONCLUSIVE",
    "neutral": "RESULT",
}
DIRECTIONS = {
    "source_to_destination": "S -> D",
    "destination_to_source": "D -> S",
    "not_stated": "DIRECTION NOT STATED",
}


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    path = Path("/usr/share/fonts/truetype/dejavu") / name
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def need_str(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a nonempty string")
    return value.strip()


def details(value: Any, name: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{name} must be a nonempty list")
    out = []
    for item in value:
        out.append(need_str(item, name))
    return out[:4]


def endpoint(path: dict[str, Any], key: str) -> dict[str, str]:
    raw = path.get(key)
    if not isinstance(raw, dict):
        raise ValueError(f"{key} must be an object")
    value = need_str(raw.get("value"), f"{key}.value")
    if "\n" in value or "\r" in value:
        raise ValueError(f"{key}.value must identify one endpoint")
    return {
        "label": str(raw.get("label") or key.title()).strip(),
        "value": value,
        "detail": str(raw.get("detail") or "").strip(),
    }


def validate(spec: dict[str, Any]) -> None:
    paths = spec.get("paths")
    if not isinstance(paths, list) or not paths:
        raise ValueError("paths must be a nonempty list")
    for p in paths:
        if not isinstance(p, dict):
            raise ValueError("each path must be an object")
        endpoint(p, "source")
        endpoint(p, "destination")
        a = p.get("assessment")
        if not isinstance(a, dict) or a.get("status") not in {"impaired", "healthy", "inconclusive", "neutral"}:
            raise ValueError("assessment.status is invalid")
        need_str(a.get("text"), "assessment.text")
        topo = p.get("topology")
        if not isinstance(topo, dict) or topo.get("mode") not in {"internal", "external"}:
            raise ValueError("topology.mode must be internal or external")
        for key in ("mtr", "iperf"):
            test = p.get(key)
            if not isinstance(test, dict):
                raise ValueError(f"{key} must be an object")
            for direction in ("source_to_destination", "destination_to_source"):
                row = test.get(direction)
                if not isinstance(row, dict) or row.get("status") not in COLORS:
                    raise ValueError(f"{key}.{direction} is invalid")
                details(row.get("details"), f"{key}.{direction}.details")


def text_width(draw: ImageDraw.ImageDraw, text: str, f: ImageFont.ImageFont) -> int:
    box = draw.textbbox((0, 0), text, font=f)
    return box[2] - box[0]


def wrap(draw: ImageDraw.ImageDraw, text: str, f: ImageFont.ImageFont, width: int) -> list[str]:
    words = str(text).split()
    if not words:
        return [""]
    lines, cur = [], words[0]
    for word in words[1:]:
        trial = f"{cur} {word}"
        if text_width(draw, trial, f) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


def dashed(draw: ImageDraw.ImageDraw, x1: int, x2: int, y: int, color: str, width: int = 4) -> None:
    step, dash = 28, 17
    for x in range(x1, x2, step):
        draw.line((x, y, min(x + dash, x2), y), fill=color, width=width)


def arrow(draw: ImageDraw.ImageDraw, x1: int, x2: int, y: int, direction: str, color: str, dash: bool = False) -> None:
    if direction == "not_stated":
        dashed(draw, x1, x2, y, color)
        return
    left_to_right = direction == "source_to_destination"
    start, end = (x1, x2) if left_to_right else (x2, x1)
    if dash:
        dashed(draw, min(start, end), max(start, end), y, color)
    else:
        draw.line((start, y, end, y), fill=color, width=4)
    sign = 1 if left_to_right else -1
    draw.polygon([(end, y), (end - sign * 15, y - 8), (end - sign * 15, y + 8)], fill=color)


def node(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str, value: str, detail: str, fonts: dict[str, Any]) -> None:
    draw.rounded_rectangle(box, 10, fill=WHITE, outline=BLACK, width=2)
    x1, y1, x2, y2 = box
    draw.text(((x1 + x2) // 2, y1 + 22), title.upper(), font=fonts["node_title"], fill=BLACK, anchor="ma")
    draw.line((x1 + 15, y1 + 48, x2 - 15, y1 + 48), fill=GRID, width=1)
    draw.text(((x1 + x2) // 2, y1 + 76), value, font=fonts["node_value"], fill=BLACK, anchor="ma")
    if detail:
        draw.text(((x1 + x2) // 2, y2 - 20), detail, font=fonts["small"], fill=DARK, anchor="ms")


def path_nodes(raw: Any) -> list[tuple[str, str]]:
    if not isinstance(raw, list):
        return []
    out = []
    for item in raw[:6]:
        if isinstance(item, str):
            out.append((item.strip(), ""))
        elif isinstance(item, dict):
            out.append((str(item.get("label") or "").strip(), str(item.get("detail") or "").strip()))
    return [(a, b) for a, b in out if a]


def draw_topology(draw: ImageDraw.ImageDraw, path: dict[str, Any], width: int, top: int, fonts: dict[str, Any]) -> int:
    src, dst = endpoint(path, "source"), endpoint(path, "destination")
    left = (50, top + 45, 390, top + 195)
    right = (width - 390, top + 45, width - 50, top + 195)
    node(draw, left, src["label"], src["value"], src["detail"], fonts)
    node(draw, right, dst["label"], dst["value"], dst["detail"], fonts)
    topo = path["topology"]
    if topo["mode"] == "internal":
        mids = path_nodes(topo.get("nodes", ["Internal network"])) or [("Internal network", "")]
        y = top + 120
        x1, x2 = 405, width - 405
        arrow(draw, x1, x2, y - 35, "source_to_destination", GREY)
        arrow(draw, x1, x2, y + 35, "destination_to_source", GREY)
        mid_w = 220
        gap = 22
        total = len(mids) * mid_w + max(0, len(mids) - 1) * gap
        start = (width - total) // 2
        for i, (label, detail) in enumerate(mids):
            x = start + i * (mid_w + gap)
            node(draw, (x, top + 70, x + mid_w, top + 170), label, detail or "", "", fonts)
        draw.text((405, y - 56), "SOURCE -> DESTINATION PATH", font=fonts["lane"], fill=DARK, anchor="ls")
        draw.text((width - 405, y + 56), "DESTINATION -> SOURCE PATH", font=fonts["lane"], fill=DARK, anchor="rs")
        return top + 230
    fwd = path_nodes(topo.get("source_to_destination", []))
    rev = path_nodes(topo.get("destination_to_source", []))
    lane_data = [(top + 82, fwd, "SOURCE -> DESTINATION TRACE", "source_to_destination"), (top + 165, rev, "DESTINATION -> SOURCE TRACE", "destination_to_source")]
    for y, nodes, title, direction in lane_data:
        draw.text((405 if direction == "source_to_destination" else width - 405, y - 30), title, font=fonts["lane"], fill=DARK, anchor="ls" if direction == "source_to_destination" else "rs")
        arrow(draw, 405, width - 405, y, direction, GREY)
        if nodes:
            cell_w = min(210, max(150, (width - 900) // len(nodes)))
            total = len(nodes) * cell_w
            start = (width - total) // 2
            for i, (label, detail) in enumerate(nodes):
                x = start + i * cell_w
                draw.rounded_rectangle((x + 5, y - 27, x + cell_w - 5, y + 27), 8, fill=WHITE, outline=GRID, width=2)
                draw.text((x + cell_w // 2, y - 5), label, font=fonts["carrier"], fill=BLACK, anchor="mm")
                if detail:
                    draw.text((x + cell_w // 2, y + 15), detail, font=fonts["tiny"], fill=DARK, anchor="mm")
        else:
            draw.text((width // 2, y), "Not provided", font=fonts["small"], fill=GREY, anchor="mm")
    return top + 245


def build_rows(path: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    reported = path.get("reported") if isinstance(path.get("reported"), list) else []
    if reported:
        for i, row in enumerate(reported, 1):
            rows.append({"label": "CLIENT REPORT" if len(reported) == 1 else f"CLIENT REPORT {i}", "status": "reported", "direction": row.get("direction", "not_stated"), "details": details(row.get("details"), "reported.details")})
    else:
        rows.append({"label": "CLIENT REPORT", "status": "not_provided", "direction": "not_stated", "details": ["No pair-specific report provided"]})
    observed = path.get("observed") if isinstance(path.get("observed"), list) else []
    if observed:
        for i, row in enumerate(observed, 1):
            status = str(row.get("status") or "neutral")
            if status not in COLORS:
                raise ValueError("observed.status is invalid")
            rows.append({"label": "OBSERVED" if len(observed) == 1 else f"OBSERVED {i}", "status": status, "direction": row.get("direction", "not_stated"), "details": details(row.get("details"), "observed.details")})
    else:
        rows.append({"label": "OBSERVED", "status": "not_provided", "direction": "not_stated", "details": ["No pair-specific observation provided"]})
    for label, group, direction in [
        ("MTR S -> D", "mtr", "source_to_destination"),
        ("MTR D -> S", "mtr", "destination_to_source"),
        ("IPERF S -> D", "iperf", "source_to_destination"),
        ("IPERF D -> S", "iperf", "destination_to_source"),
    ]:
        row = path[group][direction]
        rows.append({"label": label, "status": row["status"], "direction": direction, "details": details(row["details"], f"{group}.{direction}.details")})
    return rows


def render_page(title: str, path: dict[str, Any], page_no: int, total: int) -> Image.Image:
    width = 1900
    fonts = {
        "title": font(29, True), "pair": font(17, True), "assessment": font(15, True),
        "node_title": font(17, True), "node_value": font(18, True), "small": font(14),
        "lane": font(15, True), "carrier": font(14, True), "tiny": font(12),
        "header": font(14, True), "row": font(15, True), "pill": font(12, True),
        "result": font(15), "legend": font(13),
    }
    scratch = Image.new("RGB", (width, 1000), WHITE)
    sd = ImageDraw.Draw(scratch)
    rows = build_rows(path)
    row_heights = []
    for row in rows:
        lines = sum(len(wrap(sd, x, fonts["result"], 620)) for x in row["details"])
        row_heights.append(max(86, 48 + lines * 22))
    topo_h = 300
    table_top = 145 + topo_h
    height = table_top + 42 + sum(row_heights) + 170
    image = Image.new("RGB", (width, height), WHITE)
    draw = ImageDraw.Draw(image)
    draw.text((width // 2, 20), title, font=fonts["title"], fill=BLACK, anchor="ma")
    src, dst = endpoint(path, "source"), endpoint(path, "destination")
    meta = f"PATH {page_no} OF {total} | SOURCE: {src['value']} | DESTINATION: {dst['value']}"
    if path.get("label"):
        meta += f" | {path['label']}"
    if path.get("context"):
        meta += f" | {path['context']}"
    draw.text((width // 2, 64), meta, font=fonts["pair"], fill=DARK, anchor="ma")
    a = path["assessment"]
    color = COLORS[a["status"]]
    draw.rounded_rectangle((50, 98, width - 50, 132), 8, fill=PALE, outline=GRID)
    draw.rectangle((50, 98, 57, 132), fill=color)
    draw.text((70, 115), f"PAIR ASSESSMENT: {a['text']}", font=fonts["assessment"], fill=color, anchor="lm")
    bottom = draw_topology(draw, path, width, 145, fonts)
    table_top = max(table_top, bottom + 25)
    cols = [(50, 270), (270, 520), (520, 880), (880, 1130), (1130, width - 50)]
    headers = ["ENTRY", "SOURCE", "TEST / TRAFFIC DIRECTION", "DESTINATION", "PAIR-SPECIFIC RESULT"]
    draw.rectangle((50, table_top, width - 50, table_top + 42), fill="#EFF2F5", outline=GRID)
    for (x1, x2), header in zip(cols, headers):
        draw.text(((x1 + x2) // 2, table_top + 21), header, font=fonts["header"], fill=DARK, anchor="mm")
        draw.line((x2, table_top, x2, table_top + 42), fill=GRID)
    y = table_top + 42
    for idx, (row, rh) in enumerate(zip(rows, row_heights)):
        fill = PALE if idx % 2 else WHITE
        draw.rectangle((50, y, width - 50, y + rh), fill=fill, outline=GRID)
        color = COLORS[row["status"]]
        draw.rectangle((50, y, 57, y + rh), fill=color)
        draw.text((68, y + 22), row["label"], font=fonts["row"], fill=BLACK, anchor="la")
        pill = LABELS[row["status"]]
        pw = text_width(draw, pill, fonts["pill"]) + 16
        draw.rounded_rectangle((68, y + 45, 68 + pw, y + 67), 6, outline=color, width=1)
        draw.text((76, y + 56), pill, font=fonts["pill"], fill=color, anchor="lm")
        draw.text(((cols[1][0] + cols[1][1]) // 2, y + rh // 2), src["value"], font=fonts["row"], fill=BLACK, anchor="mm")
        draw.text(((cols[3][0] + cols[3][1]) // 2, y + rh // 2), dst["value"], font=fonts["row"], fill=BLACK, anchor="mm")
        d = row["direction"] if row["direction"] in DIRECTIONS else "not_stated"
        draw.text(((cols[2][0] + cols[2][1]) // 2, y + 24), DIRECTIONS[d], font=fonts["header"], fill=color, anchor="mm")
        arrow(draw, cols[2][0] + 24, cols[2][1] - 24, y + rh // 2 + 12, d, color, row["status"] in {"reported", "not_provided"})
        result_lines: list[str] = []
        for detail in row["details"]:
            result_lines.extend(wrap(draw, detail, fonts["result"], cols[4][1] - cols[4][0] - 35))
        draw.multiline_text((cols[4][0] + 20, y + rh // 2), "\n".join(result_lines), font=fonts["result"], fill=GREY if row["status"] == "not_provided" else BLACK, anchor="lm", spacing=4)
        for _, x2 in cols[:-1]:
            draw.line((x2, y, x2, y + rh), fill=GRID)
        y += rh
    notes = path.get("notes") if isinstance(path.get("notes"), list) else []
    if notes:
        draw.text((50, y + 20), "PAIR NOTES", font=fonts["header"], fill=DARK, anchor="la")
        y += 45
        for note in notes[:3]:
            draw.text((50, y), f"- {str(note)}", font=fonts["small"], fill=DARK, anchor="la")
            y += 24
    legend_y = height - 26
    draw.line((0, legend_y - 22, width, legend_y - 22), fill=GRID, width=2)
    legend = "Blue dashed = client report | Red = impaired | Green = working | Grey dashed = not provided | Every arrow is one direction only"
    draw.text((width // 2, legend_y), legend, font=fonts["legend"], fill=DARK, anchor="mm")
    return image


def render(spec: dict[str, Any], output: Path) -> None:
    validate(spec)
    paths = spec["paths"]
    title = str(spec.get("title") or "Network ticket triage").strip()
    pages = [render_page(title, path, i + 1, len(paths)) for i, path in enumerate(paths)]
    output.parent.mkdir(parents=True, exist_ok=True)
    suffix = output.suffix.lower()
    if suffix == ".png":
        if len(pages) != 1:
            raise ValueError("multi-pair specifications require PDF output")
        pages[0].save(output, "PNG", optimize=True)
    elif suffix == ".pdf":
        pages[0].save(output, "PDF", resolution=150, save_all=True, append_images=pages[1:])
    else:
        raise ValueError("output must end in .png or .pdf")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        with Path(args.spec).open("r", encoding="utf-8") as handle:
            spec = json.load(handle)
        render(spec, Path(args.output))
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        print(f"render_path_diagram.py: {exc}", file=sys.stderr)
        return 2
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
