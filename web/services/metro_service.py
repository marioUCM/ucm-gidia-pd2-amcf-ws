import html
import json
import folium
import pandas as pd
from utils.read_from_minio import get_minio_object_last_modified,load_json_from_minio,load_parquet_from_minio
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "../../web/static"
GENERATED_STATIC_DIR = STATIC_DIR / "generated"
METRO_MAP_DATA_PATH = STATIC_DIR / "metro_map_layers.json"
METRO_MAP_CACHE_FILENAME = "generated/metro_prediction_map.html"
METRO_MAP_CACHE_PATH = STATIC_DIR / METRO_MAP_CACHE_FILENAME

### LOCAL
# SNAPSHOT_PATH_LOCAL = BASE_DIR / "../../data/final_models/subway/subway_produccion/latest_snapshot.parquet"
# METRICS_PATH_LOCAL = BASE_DIR / "../../data/final_models/subway/subway_produccion/metrics.json"
# IMPORTANCE_PATH_LOCAL = BASE_DIR / "../../data/final_models/subway/subway_produccion/feature_importance_alert.json"

### MINIO
SNAPSHOT_PATH_MINIO = "boostmobility/final_models/subway/subway_produccion/latest_snapshot.parquet"
METRICS_PATH_MINIO = "boostmobility/final_models/subway/subway_produccion/metrics.json"
IMPORTANCE_PATH_MINIO = "boostmobility/final_models/subway/subway_produccion/feature_importance_alert.json"

METRO_LINE_GROUPS = [
    {
        "name": "Rojo",
        "family": "Broadway-7th Av",
        "lines": ["1", "2", "3"],
        "color": "#d82233",
        "description": "Lineas 1, 2 y 3.",
    },
    {
        "name": "Verde",
        "family": "Lexington Av",
        "lines": ["4", "5", "6"],
        "color": "#009952",
        "description": "Lineas 4, 5 y 6.",
    },
    {
        "name": "Morado",
        "family": "Flushing",
        "lines": ["7"],
        "color": "#9a38a1",
        "description": "Linea 7.",
    },
    {
        "name": "Azul",
        "family": "8th Av",
        "lines": ["A", "C", "E"],
        "color": "#0062cf",
        "description": "Lineas A, C y E.",
    },
    {
        "name": "Naranja",
        "family": "6th Av",
        "lines": ["B", "D", "F", "M"],
        "color": "#eb6800",
        "description": "Lineas B, D, F y M.",
    },
    {
        "name": "Amarillo",
        "family": "Broadway",
        "lines": ["N", "Q", "R", "W"],
        "color": "#f6bc26",
        "description": "Lineas N, Q, R y W.",
    },
    {
        "name": "Gris",
        "family": "Canarsie",
        "lines": ["L"],
        "color": "#7c858c",
        "description": "Linea L.",
    },
    {
        "name": "Verde lima",
        "family": "Crosstown",
        "lines": ["G"],
        "color": "#799534",
        "description": "Linea G.",
    },
    {
        "name": "Marron",
        "family": "Nassau St",
        "lines": ["J", "Z"],
        "color": "#8e5c33",
        "description": "Lineas J y Z.",
    },
    {
        "name": "Shuttle",
        "family": "Lanzaderas",
        "lines": ["S", "S 42ND", "S FKLN", "S ROCK"],
        "color": "#4b5563",
        "description": "Servicios shuttle y lanzaderas.",
    },
]


def _read_json(path: Path | str, default_value):
    if isinstance(path, Path):
        if not path.exists():
            return default_value
        return json.loads(path.read_text(encoding="utf-8"))

    try:
        return load_json_from_minio(path)         # MINIO
        # return pd.read_json(path)               # LOCAL
    except Exception:  
        return default_value


def _safe_mtime(path: Path | str) -> float:
    if isinstance(path, Path):
        return path.stat().st_mtime if path.exists() else 0.0

    last_modified = get_minio_object_last_modified(path)
    if last_modified is None:
        return 0.0
    return last_modified.timestamp()


def _format_datetime(value):
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d %H:%M")
    return value


def _line_label_text_color(color: str) -> str:
    return "#111111" if color.upper() in {"#F6BC26", "#FFD60A"} else "#FFFFFF"


def _line_badge_html(label: str, color: str) -> str:
    text_color = _line_label_text_color(color)
    safe_label = html.escape(label)
    return f"""
        <div style="
            width: 26px;
            height: 26px;
            border-radius: 999px;
            background: {color};
            border: 2px solid rgba(255, 255, 255, 0.95);
            box-shadow: 0 6px 14px rgba(15, 23, 42, 0.28);
            color: {text_color};
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: Inter, Arial, sans-serif;
            font-size: 12px;
            font-weight: 800;
            line-height: 1;
        ">{safe_label}</div>
    """


def _probability_badge_html(label: str, color: str, probability: float) -> str:
    text_color = _line_label_text_color(color)
    safe_label = html.escape(label)
    percent = f"{probability * 100:.1f}%"
    return f"""
        <div style="
            display: inline-flex;
            align-items: center;
            gap: 10px;
            min-width: 120px;
            padding: 6px 10px 6px 6px;
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid rgba(208, 220, 233, 0.95);
            box-shadow: 0 10px 18px rgba(15, 23, 42, 0.18);
            font-family: Inter, Arial, sans-serif;
            white-space: nowrap;
        ">
            <span style="
                width: 28px;
                height: 28px;
                border-radius: 999px;
                background: {color};
                color: {text_color};
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                font-weight: 800;
                border: 2px solid rgba(255, 255, 255, 0.95);
            ">{safe_label}</span>
            <span style="display: flex; flex-direction: column; gap: 3px;">
                <span style="
                    color: #0f172a;
                    font-size: 11px;
                    font-weight: 700;
                    letter-spacing: 0.2px;
                    text-transform: uppercase;
                ">riesgo</span>
                <span style="
                    color: #0f172a;
                    font-size: 13px;
                    font-weight: 800;
                    letter-spacing: 0.2px;
                ">{percent}</span>
                <span style="
                    display: block;
                    width: 64px;
                    height: 6px;
                    border-radius: 999px;
                    background: rgba(148, 163, 184, 0.22);
                    overflow: hidden;
                ">
                    <span style="
                        display: block;
                        width: {max(12.0, probability * 100):.1f}%;
                        height: 100%;
                        border-radius: 999px;
                        background: linear-gradient(90deg, {color} 0%, rgba(255,255,255,0.92) 100%);
                    "></span>
                </span>
            </span>
        </div>
    """


def _probability_badge_tooltip(label: str, color: str, probability: float) -> folium.Tooltip:
    return folium.Tooltip(
        _probability_badge_html(label, color, probability),
        sticky=False,
        direction="top",
        style=(
            "background: transparent; border: none; box-shadow: none; padding: 0;"
            "font-family: Inter, Arial, sans-serif;"
        ),
    )


def _attach_map_bounds(
    root_object: folium.Figure,
    map_name: str,
    bounds: list[list[float]],
    min_zoom: int = 11,
) -> None:
    bounds_json = json.dumps(bounds)
    map_name_json = json.dumps(map_name)
    min_zoom_json = json.dumps(min_zoom)
    script = f"""
        (function() {{
            const mapVarName = {map_name_json};
            function applyBounds() {{
                const map = window[mapVarName];
                if (!map) {{
                    window.setTimeout(applyBounds, 60);
                    return;
                }}
                map.setMaxBounds({bounds_json});
                map.setMinZoom({min_zoom_json});
                map.options.maxBoundsViscosity = 1.0;
            }}
            applyBounds();
        }})();
    """
    root_object.get_root().script.add_child(folium.Element(script))


def _resolve_map_line_metrics(line_id: str, snapshot: pd.DataFrame | None) -> dict[str, float | str] | None:
    if snapshot is None or snapshot.empty:
        return None

    if line_id == "JZ":
        subset = snapshot[snapshot["line"].astype(str).isin(["J", "Z"])].copy()
        label = "J/Z"
    else:
        subset = snapshot[snapshot["line"].astype(str) == line_id].copy()
        label = line_id

    if subset.empty:
        return None

    lead_row = subset.sort_values(["alert_prob_next_60m", "rank"], ascending=[False, True]).iloc[0]
    return {
        "label": label,
        "line": label,
        "alert_prob_next_60m": float(subset["alert_prob_next_60m"].max()),
        "delay_prob_next_60m": float(subset["delay_prob_next_60m"].max()),
        "suspension_prob_next_60m": float(subset["suspension_prob_next_60m"].max()),
        "risk_index": float(subset["risk_index"].max()),
        "risk_level": str(lead_row["risk_level"]),
    }


def _build_map_line_variants(line_id: str, snapshot: pd.DataFrame | None) -> list[dict[str, float | str]]:
    if snapshot is None or snapshot.empty:
        return []
    if line_id != "JZ":
        return []

    variants = []
    for subline in ["J", "Z"]:
        metrics = _resolve_map_line_metrics(subline, snapshot)
        if metrics is not None:
            variants.append(metrics)
    return variants


def _offset_location(lat: float, lon: float, variant_idx: int, total_variants: int) -> list[float]:
    base_shift = (variant_idx - ((total_variants - 1) / 2)) * 0.0022
    return [lat + base_shift, lon + (base_shift * 0.65)]


def _build_map_tooltip_html(
    line_id: str,
    default_label: str,
    line_metrics: dict[str, float | str] | None,
    line_variants: list[dict[str, float | str]],
) -> str:
    base_style = (
        "background-color: white; color: #18212c; font-family: Inter, Arial, sans-serif; "
        "font-size: 12px; padding: 8px 10px; border-radius: 10px; border: 1px solid #d7e1eb;"
    )
    if line_variants:
        rows = []
        for variant in line_variants:
            rows.append(
                "<div style='display:flex; justify-content:space-between; gap:10px;'>"
                f"<strong>{html.escape(str(variant['line']))}</strong>"
                f"<span>{float(variant['alert_prob_next_60m']) * 100:.1f}%</span>"
                "</div>"
            )
        return (
            f"<div style='{base_style}'>"
            "<div style='font-weight:800; margin-bottom:6px;'>Servicios J y Z</div>"
            + "".join(rows)
            + "</div>"
        )
    if line_metrics:
        return (
            f"<div style='{base_style}'>"
            f"<div style='font-weight:800; margin-bottom:6px;'>Linea {html.escape(str(line_metrics['label']))}</div>"
            f"<div>Riesgo {float(line_metrics['alert_prob_next_60m']) * 100:.1f}%</div>"
            f"<div>Delay {float(line_metrics['delay_prob_next_60m']) * 100:.1f}%</div>"
            f"<div>Suspension {float(line_metrics['suspension_prob_next_60m']) * 100:.1f}%</div>"
            "</div>"
        )
    if line_id == "JZ":
        return f"<div style='{base_style}'>Servicios J y Z</div>"
    return f"<div style='{base_style}'>Linea {html.escape(default_label)}</div>"


def _add_probability_signal(
    target_group: folium.FeatureGroup,
    location: list[float],
    color: str,
    probability: float,
) -> None:
    radius = 7 + (probability * 18)
    fill_opacity = 0.10 + (probability * 0.22)
    opacity = 0.28 + (probability * 0.38)
    folium.CircleMarker(
        location=location,
        radius=radius,
        color=color,
        weight=2,
        opacity=opacity,
        fill=True,
        fill_color=color,
        fill_opacity=fill_opacity,
        interactive=False,
    ).add_to(target_group)
    folium.CircleMarker(
        location=location,
        radius=max(3.2, radius * 0.38),
        color="#FFFFFF",
        weight=1,
        opacity=0.82,
        fill=True,
        fill_color="#FFFFFF",
        fill_opacity=0.86,
        interactive=False,
    ).add_to(target_group)


def _polyline_length(path: list[list[float]]) -> float:
    total = 0.0
    for start, end in zip(path, path[1:]):
        total += ((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2) ** 0.5
    return total


def _normalize_point_key(lat: float, lon: float, precision: int = 5) -> tuple[float, float]:
    return (round(float(lat), precision), round(float(lon), precision))


def _point_line_labels(line_id: str, default_label: str) -> list[str]:
    if line_id == "JZ":
        return ["J", "Z"]
    return [str(default_label)]


def _build_point_lines_lookup(map_data: dict) -> dict[tuple[float, float], list[str]]:
    lookup: dict[tuple[float, float], set[str]] = {}
    for line in map_data.get("lines", []):
        line_id = str(line.get("id", ""))
        line_labels = _point_line_labels(line_id, str(line.get("label", line_id)))
        for path in line.get("paths", []):
            for point in path:
                if len(point) < 2:
                    continue
                key = _normalize_point_key(point[0], point[1])
                if key not in lookup:
                    lookup[key] = set()
                lookup[key].update(line_labels)

    return {key: sorted(values) for key, values in lookup.items()}


def _build_station_tooltip_html(station_name: str, line_labels: list[str] | None) -> str:
    base_style = (
        "background-color: white; color: #18212c; font-family: Inter, Arial, sans-serif; "
        "font-size: 12px; padding: 8px 10px; border-radius: 8px; border: 1px solid #d7e1eb;"
    )
    if line_labels:
        joined_lines = ", ".join(html.escape(label) for label in line_labels)
        return (
            f"<div style='{base_style}'>"
            f"<div style='font-weight:800; margin-bottom:6px;'>{html.escape(station_name)}</div>"
            f"<div>Lineas: {joined_lines}</div>"
            "</div>"
        )
    return f"<div style='{base_style}'>{html.escape(station_name)}</div>"


def _resolve_station_lines(
    lat: float,
    lon: float,
    point_lines_lookup: dict[tuple[float, float], list[str]],
    threshold: float = 0.0018,
) -> list[str]:
    exact_match = point_lines_lookup.get(_normalize_point_key(lat, lon))
    if exact_match:
        return exact_match

    nearby_labels: set[str] = set()
    for (point_lat, point_lon), labels in point_lines_lookup.items():
        distance = ((float(lat) - point_lat) ** 2 + (float(lon) - point_lon) ** 2) ** 0.5
        if distance <= threshold:
            nearby_labels.update(labels)

    return sorted(nearby_labels)


def _build_train_animation_specs(map_data: dict, snapshot: pd.DataFrame | None) -> list[dict[str, object]]:
    map_lines = {
        str(line["id"]): line
        for line in map_data.get("lines", [])
        if line.get("paths")
    }
    selected_ids: list[str] = []

    if snapshot is not None and not snapshot.empty:
        for line_id in snapshot.sort_values("alert_prob_next_60m", ascending=False)["line"].astype(str):
            if line_id in map_lines and line_id not in selected_ids:
                selected_ids.append(line_id)
            elif line_id in {"J", "Z"} and "JZ" in map_lines and "JZ" not in selected_ids:
                selected_ids.append("JZ")

    for fallback_id in ["7", "A", "4", "N", "L", "G", "E", "1", "JZ"]:
        if fallback_id in map_lines and fallback_id not in selected_ids:
            selected_ids.append(fallback_id)

    specs: list[dict[str, object]] = []
    for idx, line_id in enumerate(selected_ids):
        if len(specs) >= 6:
            break
        if line_id == "JZ":
            continue
        line = map_lines[line_id]
        longest_path = max(line.get("paths", []), key=_polyline_length, default=None)
        if not longest_path or len(longest_path) < 2:
            continue
        dwell_count = min(4, max(2, len(longest_path) // 10))
        specs.append(
            {
                "color": str(line["color"]),
                "path": longest_path,
                "duration_ms": 15000 + (idx * 1400),
                "pause_ms": 2200 + (idx * 320),
                "pause_jitter_ms": 1300,
                "initial_delay_ms": 450 + (idx * 760),
                "initial_delay_jitter_ms": 1800 + (idx * 220),
                "stop_ms": 950 + min(idx, 3) * 110,
                "stop_jitter_ms": 480,
                "stop_count_min": max(1, dwell_count - 1),
                "stop_count_max": dwell_count + 1,
            }
        )
    return specs


def _attach_animated_trains(root_object: folium.Figure, map_name: str, specs: list[dict[str, object]]) -> None:
    if not specs:
        return

    map_name_json = json.dumps(map_name)
    specs_json = json.dumps(specs)
    script = f"""
        (function() {{
            const mapVarName = {map_name_json};
            const trainSpecs = {specs_json};

            function distance(a, b) {{
                const dx = b[0] - a[0];
                const dy = b[1] - a[1];
                return Math.sqrt((dx * dx) + (dy * dy));
            }}

            function buildSegments(path) {{
                const segments = [];
                let total = 0;
                for (let i = 0; i < path.length - 1; i += 1) {{
                    const start = path[i];
                    const end = path[i + 1];
                    const length = distance(start, end);
                    if (!length) continue;
                    segments.push({{ start, end, length, startOffset: total }});
                    total += length;
                }}
                return {{ total, segments }};
            }}

            function stateAt(prepared, progress) {{
                if (!prepared.segments.length) return null;
                const target = prepared.total * Math.min(Math.max(progress, 0), 1);
                for (const segment of prepared.segments) {{
                    const segmentEnd = segment.startOffset + segment.length;
                    if (target <= segmentEnd) {{
                        const localProgress = (target - segment.startOffset) / segment.length;
                        const lat = segment.start[0] + ((segment.end[0] - segment.start[0]) * localProgress);
                        const lon = segment.start[1] + ((segment.end[1] - segment.start[1]) * localProgress);
                        const angle = Math.atan2(
                            -(segment.end[0] - segment.start[0]),
                            segment.end[1] - segment.start[1]
                        ) * (180 / Math.PI);
                        return {{
                            point: [lat, lon],
                            angle,
                        }};
                    }}
                }}
                const last = prepared.segments[prepared.segments.length - 1];
                if (!last) return null;
                return {{
                    point: last.end,
                    angle: Math.atan2(
                        -(last.end[0] - last.start[0]),
                        last.end[1] - last.start[1]
                    ) * (180 / Math.PI),
                }};
            }}

            function trainIcon(spec) {{
                return L.divIcon({{
                    className: '',
                    iconSize: [46, 22],
                    iconAnchor: [23, 11],
                    html: `
                        <div style="
                            width: 46px;
                            height: 22px;
                            display: flex;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            pointer-events: none;
                        ">
                            <div class="metro-train-shape" style="
                                width: 46px;
                                height: 22px;
                                position: relative;
                                transform-origin: 50% 50%;
                                filter: drop-shadow(0 4px 8px rgba(15, 23, 42, 0.22));
                            ">
                                <div style="
                                    position: absolute;
                                    left: 0;
                                    top: 7px;
                                    width: 12px;
                                    height: 8px;
                                    background: rgba(255,255,255,0.98);
                                    clip-path: polygon(0 50%, 100% 0, 100% 100%);
                                    border-top-left-radius: 3px;
                                    border-bottom-left-radius: 3px;
                                    border: 1px solid rgba(186, 151, 91, 0.58);
                                    border-right: none;
                                    box-sizing: border-box;
                                "></div>
                                <div style="
                                    position: absolute;
                                    left: 9px;
                                    top: 5px;
                                    width: 11px;
                                    height: 10px;
                                    background: linear-gradient(180deg, #fffdf7 0%, #f2ece0 100%);
                                    border: 1px solid rgba(186, 151, 91, 0.58);
                                    border-radius: 3px 3px 2px 2px;
                                    box-sizing: border-box;
                                ">
                                    <div style="
                                        position: absolute;
                                        left: 2px;
                                        top: 2px;
                                        width: 2px;
                                        height: 3px;
                                        background: rgba(115, 146, 161, 0.82);
                                        border-radius: 1px;
                                    "></div>
                                    <div style="
                                        position: absolute;
                                        right: 2px;
                                        top: 2px;
                                        width: 2px;
                                        height: 3px;
                                        background: rgba(115, 146, 161, 0.82);
                                        border-radius: 1px;
                                    "></div>
                                </div>
                                <div style="
                                    position: absolute;
                                    left: 18px;
                                    top: 4px;
                                    width: 24px;
                                    height: 12px;
                                    background: linear-gradient(180deg, #fffdf8 0%, #f3efe5 100%);
                                    border: 1px solid rgba(186, 151, 91, 0.58);
                                    border-radius: 7px 7px 6px 6px;
                                    box-sizing: border-box;
                                    overflow: hidden;
                                ">
                                    <div style="
                                        position: absolute;
                                        inset: 0;
                                        background: linear-gradient(90deg, rgba(255,255,255,0.0) 0%, ${{spec.color}} 42%, ${{spec.color}} 100%);
                                        opacity: 0.94;
                                    "></div>
                                    <div style="
                                        position: absolute;
                                        left: 3px;
                                        top: 3px;
                                        width: 3px;
                                        height: 3px;
                                        border-radius: 999px;
                                        background: rgba(115, 146, 161, 0.86);
                                        border: 1px solid rgba(255,255,255,0.72);
                                    "></div>
                                    <div style="
                                        position: absolute;
                                        left: 9px;
                                        top: 3px;
                                        width: 3px;
                                        height: 3px;
                                        border-radius: 999px;
                                        background: rgba(115, 146, 161, 0.86);
                                        border: 1px solid rgba(255,255,255,0.72);
                                    "></div>
                                    <div style="
                                        position: absolute;
                                        left: 15px;
                                        top: 3px;
                                        width: 3px;
                                        height: 3px;
                                        border-radius: 999px;
                                        background: rgba(115, 146, 161, 0.86);
                                        border: 1px solid rgba(255,255,255,0.72);
                                    "></div>
                                </div>
                                <div style="
                                    position: absolute;
                                    left: 7px;
                                    top: 16px;
                                    width: 30px;
                                    height: 3px;
                                    background: rgba(0, 0, 0, 0.08);
                                    border-radius: 999px;
                                "></div>
                                <div style="
                                    position: absolute;
                                    left: 8px;
                                    top: 16px;
                                    width: 5px;
                                    height: 5px;
                                    border-radius: 999px;
                                    background: #81848b;
                                    border: 1px solid rgba(255,255,255,0.72);
                                    box-sizing: border-box;
                                "></div>
                                <div style="
                                    position: absolute;
                                    left: 18px;
                                    top: 16px;
                                    width: 5px;
                                    height: 5px;
                                    border-radius: 999px;
                                    background: #81848b;
                                    border: 1px solid rgba(255,255,255,0.72);
                                    box-sizing: border-box;
                                "></div>
                                <div style="
                                    position: absolute;
                                    left: 29px;
                                    top: 16px;
                                    width: 5px;
                                    height: 5px;
                                    border-radius: 999px;
                                    background: #81848b;
                                    border: 1px solid rgba(255,255,255,0.72);
                                    box-sizing: border-box;
                                "></div>
                                <div style="
                                    position: absolute;
                                    left: 39px;
                                    top: 16px;
                                    width: 5px;
                                    height: 5px;
                                    border-radius: 999px;
                                    background: #81848b;
                                    border: 1px solid rgba(255,255,255,0.72);
                                    box-sizing: border-box;
                                "></div>
                            </div>
                        </div>
                    `,
                }});
            }}

            function setTrainAngle(marker, angle) {{
                const markerElement = marker.getElement();
                if (!markerElement) return;
                const shape = markerElement.querySelector('.metro-train-shape');
                if (shape) {{
                    shape.style.transform = `rotate(${{angle}}deg)`;
                }}
            }}

            function randomBetween(min, max) {{
                return min + (Math.random() * (max - min));
            }}

            function randomInt(min, max) {{
                const safeMin = Math.ceil(min);
                const safeMax = Math.floor(max);
                return Math.floor(randomBetween(safeMin, safeMax + 1));
            }}

            function buildRandomStops(spec) {{
                const stopCount = randomInt(
                    Math.max(0, spec.stop_count_min || 0),
                    Math.max(0, spec.stop_count_max || spec.stop_count_min || 0)
                );

                if (!stopCount) {{
                    return [];
                }}

                const rawStops = [];
                for (let index = 0; index < stopCount; index += 1) {{
                    rawStops.push(randomBetween(0.12, 0.88));
                }}

                rawStops.sort(function (a, b) {{
                    return a - b;
                }});

                const spacedStops = [];
                rawStops.forEach(function (stop, index) {{
                    const previousStop = index === 0 ? 0.05 : spacedStops[index - 1];
                    const adjustedStop = Math.max(stop, previousStop + 0.08);
                    if (adjustedStop < 0.94) {{
                        spacedStops.push(Number(adjustedStop.toFixed(3)));
                    }}
                }});

                return spacedStops;
            }}

            function computeLaunchDelay(spec, baseDelayMs) {{
                return Math.max(
                    0,
                    baseDelayMs + randomBetween(0, Math.max(0, spec.initial_delay_jitter_ms || 0))
                );
            }}

            function launchTrain(mapInstance, spec, delayMs) {{
                window.setTimeout(function () {{
                    const prepared = buildSegments(spec.path);
                    if (!prepared.total) return;

                    const startState = stateAt(prepared, 0);
                    if (!startState) return;

                    const marker = L.marker(startState.point, {{
                        icon: trainIcon(spec),
                        interactive: false,
                        keyboard: false,
                        zIndexOffset: 1200,
                        opacity: 0,
                    }}).addTo(mapInstance);

                    const duration = spec.duration_ms;
                    const fadeWindow = 0.15;
                    const startedAt = performance.now();
                    const stopProgresses = buildRandomStops(spec);
                    const stopDurationMs = Math.max(
                        0,
                        (spec.stop_ms || 0) + randomBetween(0, Math.max(0, spec.stop_jitter_ms || 0))
                    );
                    let nextStopIndex = 0;
                    let pausedTotal = 0;
                    let holdUntil = 0;
                    let pendingStopMs = 0;

                    function frame(now) {{
                        if (holdUntil && now < holdUntil) {{
                            window.requestAnimationFrame(frame);
                            return;
                        }}

                        if (holdUntil && now >= holdUntil) {{
                            pausedTotal += pendingStopMs;
                            holdUntil = 0;
                            pendingStopMs = 0;
                        }}

                        const progress = Math.min((now - startedAt - pausedTotal) / duration, 1);
                        const currentState = stateAt(prepared, progress);
                        if (currentState) {{
                            marker.setLatLng(currentState.point);
                            setTrainAngle(marker, currentState.angle);
                        }}

                        let opacity = 1;
                        if (progress < fadeWindow) {{
                            opacity = progress / fadeWindow;
                        }} else if (progress > (1 - fadeWindow)) {{
                            opacity = (1 - progress) / fadeWindow;
                        }}
                        marker.setOpacity(Math.max(0, Math.min(1, opacity)));

                        if (
                            nextStopIndex < stopProgresses.length &&
                            progress >= stopProgresses[nextStopIndex] &&
                            progress < 0.98
                        ) {{
                            pendingStopMs = stopDurationMs;
                            holdUntil = now + pendingStopMs;
                            nextStopIndex += 1;
                            window.requestAnimationFrame(frame);
                            return;
                        }}

                        if (progress < 1) {{
                            window.requestAnimationFrame(frame);
                        }} else {{
                            marker.remove();
                            const nextDelay = spec.pause_ms + Math.random() * spec.pause_jitter_ms;
                            launchTrain(mapInstance, spec, nextDelay);
                        }}
                    }}

                    setTrainAngle(marker, startState.angle);
                    window.requestAnimationFrame(frame);
                }}, delayMs);
            }}

            function startWhenMapReady() {{
                const map = window[mapVarName];
                if (!map) {{
                    window.setTimeout(startWhenMapReady, 60);
                    return;
                }}

                trainSpecs.forEach(function (spec) {{
                    launchTrain(map, spec, computeLaunchDelay(spec, spec.initial_delay_ms || 0));
                }});
            }}

            startWhenMapReady();
        }})();
    """
    root_object.get_root().script.add_child(folium.Element(script))


def _attach_line_focus_controls(
    root_object: folium.Figure,
    map_name: str,
    line_layers: dict[str, dict[str, object]],
) -> None:
    if not line_layers:
        return

    map_name_json = json.dumps(map_name)
    line_layers_json = json.dumps(line_layers)
    script = f"""
        (function() {{
            const mapVarName = {map_name_json};
            const lineLayers = {line_layers_json};
            const aliasMap = {{
                J: 'JZ',
                Z: 'JZ'
            }};
            let activeLineId = null;

            function getMap() {{
                return window[mapVarName];
            }}

            function getLayer(layerName) {{
                return window[layerName] || null;
            }}

            function resolveLineId(rawLineId) {{
                if (!rawLineId) return null;
                if (lineLayers[rawLineId]) return rawLineId;
                return aliasMap[rawLineId] && lineLayers[aliasMap[rawLineId]] ? aliasMap[rawLineId] : rawLineId;
            }}

            function applyStyle(layer, color, weight, opacity) {{
                if (!layer || !layer.setStyle) return;
                layer.setStyle({{
                    color: color,
                    weight: weight,
                    opacity: opacity,
                }});
            }}

            function bringLineToFront(lineId) {{
                const config = lineLayers[lineId];
                if (!config) return;

                ['glow', 'main', 'rail'].forEach(function (layerGroup) {{
                    (config[layerGroup] || []).forEach(function (layerName) {{
                        const layer = getLayer(layerName);
                        if (layer && layer.bringToFront) {{
                            layer.bringToFront();
                        }}
                    }});
                }});
            }}

            function styleLine(lineId, isSelected, hasSelection) {{
                const config = lineLayers[lineId];
                if (!config) return;

                const fadeMainColor = '#b8c2cc';
                const fadeGlowColor = '#d5dbe2';
                const fadeRailColor = '#eef2f6';

                (config.glow || []).forEach(function (layerName) {{
                    const layer = getLayer(layerName);
                    if (!hasSelection) {{
                        applyStyle(layer, config.color, config.glow_weight, config.glow_opacity);
                    }} else if (isSelected) {{
                        applyStyle(layer, config.color, config.glow_weight + 1.4, Math.max(config.glow_opacity, 0.22));
                    }} else {{
                        applyStyle(layer, fadeGlowColor, Math.max(1.6, config.glow_weight * 0.72), 0.055);
                    }}
                }});

                (config.main || []).forEach(function (layerName) {{
                    const layer = getLayer(layerName);
                    if (!hasSelection) {{
                        applyStyle(layer, config.color, config.main_weight, config.main_opacity);
                    }} else if (isSelected) {{
                        applyStyle(layer, config.color, config.main_weight + 1.1, Math.max(config.main_opacity, 0.92));
                    }} else {{
                        applyStyle(layer, fadeMainColor, Math.max(1.6, config.main_weight * 0.9), 0.24);
                    }}
                }});

                (config.rail || []).forEach(function (layerName) {{
                    const layer = getLayer(layerName);
                    if (!hasSelection) {{
                        applyStyle(layer, '#FFFFFF', config.rail_weight, config.rail_opacity);
                    }} else if (isSelected) {{
                        applyStyle(layer, '#FFFFFF', config.rail_weight, Math.max(config.rail_opacity, 0.46));
                    }} else {{
                        applyStyle(layer, fadeRailColor, config.rail_weight, 0.1);
                    }}
                }});
            }}

            function applySelection(rawLineId) {{
                const nextLineId = resolveLineId(rawLineId);
                const hasSelection = !!(nextLineId && lineLayers[nextLineId]);
                activeLineId = hasSelection ? nextLineId : null;

                Object.keys(lineLayers).forEach(function (lineId) {{
                    styleLine(lineId, lineId === activeLineId, hasSelection);
                }});

                if (activeLineId) {{
                    bringLineToFront(activeLineId);
                }}

                if (window.parent && window.parent !== window) {{
                    window.parent.postMessage(
                        {{
                            type: 'metro-map-selection-changed',
                            lineId: activeLineId
                        }},
                        window.location.origin
                    );
                }}
            }}

            function registerClicks() {{
                Object.entries(lineLayers).forEach(function ([lineId, config]) {{
                    (config.main || []).forEach(function (layerName) {{
                        const layer = getLayer(layerName);
                        if (!layer || !layer.on) return;
                        layer.on('click', function () {{
                            applySelection(lineId);
                        }});
                    }});
                }});
            }}

            function initialize() {{
                const map = getMap();
                if (!map) {{
                    window.setTimeout(initialize, 60);
                    return;
                }}

                registerClicks();
                map.on('click', function () {{
                    applySelection(null);
                }});

                window.addEventListener('message', function (event) {{
                    const data = event && event.data ? event.data : null;
                    if (!data || data.type !== 'metro-map-focus-line') return;
                    applySelection(data.lineId || null);
                }});
            }}

            initialize();
        }})();
    """
    root_object.get_root().script.add_child(folium.Element(script))


def _generate_metro_prediction_map(snapshot: pd.DataFrame | None = None) -> str | None:
    map_data = _read_json(METRO_MAP_DATA_PATH, None)
    if not map_data:
        return None

    figure = folium.Figure(width="100%", height="720px")
    metro_map = folium.Map(
        location=map_data.get("center", [40.7282, -73.9418]),
        zoom_start=11,
        min_zoom=11,
        max_zoom=14,
        max_bounds=True,
        control_scale=True,
        zoom_control=True,
        prefer_canvas=True,
        tiles="CartoDB Positron",
        width="100%",
        height="100%",
    )

    bounds = map_data.get("bounds")
    if bounds:
        metro_map.fit_bounds(bounds)

    lines_group = folium.FeatureGroup(name="Lineas", show=True)
    stations_group = folium.FeatureGroup(name="Estaciones", show=True)

    snapshot_max = 0.0
    if snapshot is not None and not snapshot.empty:
        snapshot_max = float(snapshot["alert_prob_next_60m"].max())

    animated_train_specs = _build_train_animation_specs(map_data, snapshot)
    point_lines_lookup = _build_point_lines_lookup(map_data)
    line_layers: dict[str, dict[str, object]] = {}

    for line in map_data.get("lines", []):
        line_id = str(line["id"])
        line_metrics = _resolve_map_line_metrics(line_id, snapshot)
        line_variants = _build_map_line_variants(line_id, snapshot)
        line_prob = 0.0 if not line_metrics else float(line_metrics["alert_prob_next_60m"])
        tooltip_html = _build_map_tooltip_html(
            line_id,
            str(line.get("label", line_id)),
            line_metrics,
            line_variants,
        )
        relative_strength = 0.0 if snapshot_max <= 0 else min(line_prob / snapshot_max, 1.0)
        line_weight = 3.2 + (relative_strength * 3.8)
        line_opacity = 0.44 + (relative_strength * 0.28)
        glow_weight = line_weight + 3.6
        glow_opacity = 0.06 + (relative_strength * 0.12)
        rail_weight = max(1.15, line_weight * 0.18)
        rail_opacity = 0.18 + (relative_strength * 0.10)

        line_layers[line_id] = {
            "color": str(line["color"]),
            "main_weight": line_weight,
            "main_opacity": line_opacity,
            "glow_weight": glow_weight,
            "glow_opacity": glow_opacity,
            "rail_weight": rail_weight,
            "rail_opacity": rail_opacity,
            "glow": [],
            "main": [],
            "rail": [],
        }

        for path in line.get("paths", []):
            glow_line = folium.PolyLine(
                locations=path,
                color=line["color"],
                weight=glow_weight,
                opacity=glow_opacity,
                line_cap="round",
                line_join="round",
                interactive=False,
            )
            glow_line.add_to(lines_group)
            line_layers[line_id]["glow"].append(glow_line.get_name())

            main_line = folium.PolyLine(
                locations=path,
                color=line["color"],
                weight=line_weight,
                opacity=line_opacity,
                line_cap="round",
                line_join="round",
                tooltip=folium.Tooltip(
                    tooltip_html,
                    sticky=False,
                    direction="top",
                ),
            )
            main_line.add_to(lines_group)
            line_layers[line_id]["main"].append(main_line.get_name())

            rail_line = folium.PolyLine(
                locations=path,
                color="#FFFFFF",
                weight=rail_weight,
                opacity=rail_opacity,
                line_cap="round",
                line_join="round",
                interactive=False,
            )
            rail_line.add_to(lines_group)
            line_layers[line_id]["rail"].append(rail_line.get_name())

    for station in map_data.get("stations", []):
        station_lines = _resolve_station_lines(
            float(station["lat"]),
            float(station["lon"]),
            point_lines_lookup,
        )
        folium.CircleMarker(
            location=[station["lat"], station["lon"]],
            radius=2.1,
            color="#1f2937",
            weight=1,
            fill=True,
            fill_color="#ffffff",
            fill_opacity=0.78,
            opacity=0.52,
            tooltip=folium.Tooltip(
                _build_station_tooltip_html(str(station["name"]), station_lines),
                sticky=False,
                direction="top",
                style=(
                    "background: transparent; border: none; box-shadow: none; padding: 0; "
                    "font-family: Inter, Arial, sans-serif;"
                ),
            ),
        ).add_to(stations_group)

    lines_group.add_to(metro_map)
    stations_group.add_to(metro_map)
    metro_map.add_to(figure)
    if bounds:
        _attach_map_bounds(figure, metro_map.get_name(), bounds, min_zoom=11)
    _attach_animated_trains(figure, metro_map.get_name(), animated_train_specs)
    _attach_line_focus_controls(figure, metro_map.get_name(), line_layers)
    return figure.render()


def _load_snapshot() -> pd.DataFrame | None:
    try:
        snapshot = load_parquet_from_minio(SNAPSHOT_PATH_MINIO)     # MINIO
        # snapshot = pd.read_parquet(SNAPSHOT_PATH_LOCAL)           # LOCAL
    except Exception:
        return None
    return snapshot.sort_values("rank").reset_index(drop=True)


def _ensure_metro_prediction_map_file(
    snapshot: pd.DataFrame | None = None,
    *,
    strict: bool = True,
) -> tuple[str | None, str | None]:
    if not METRO_MAP_DATA_PATH.exists():
        if strict:
            raise FileNotFoundError(
                f"No existe el archivo de capas del mapa de metro: {METRO_MAP_DATA_PATH}"
            )
        return None, None

    source_mtime = max(
        _safe_mtime(METRO_MAP_DATA_PATH),
        _safe_mtime(SNAPSHOT_PATH_MINIO),                           # MINIO
        # _safe_mtime(SNAPSHOT_PATH_LOCAL),                         # LOCAL
        _safe_mtime(Path(__file__)),
    )
    cache_mtime = _safe_mtime(METRO_MAP_CACHE_PATH)

    if not METRO_MAP_CACHE_PATH.exists() or cache_mtime < source_mtime:
        map_html = _generate_metro_prediction_map(snapshot)
        if map_html is None:
            if strict:
                raise RuntimeError(
                    "No se pudo generar el mapa interactivo de metro con los datos disponibles."
                )
            return None, None
        GENERATED_STATIC_DIR.mkdir(parents=True, exist_ok=True)
        METRO_MAP_CACHE_PATH.write_text(map_html, encoding="utf-8")

    version = str(int(source_mtime)) if source_mtime else None
    return METRO_MAP_CACHE_FILENAME, version


def initialize_metro_dashboard_assets() -> None:
    snapshot = _load_snapshot()
    _ensure_metro_prediction_map_file(snapshot, strict=True)


def _build_line_group_cards(snapshot: pd.DataFrame) -> list[dict]:
    if snapshot.empty:
        return []

    cards = []
    for group in METRO_LINE_GROUPS:
        group_df = snapshot[snapshot["line"].astype(str).isin(group["lines"])].copy()
        if group_df.empty:
            continue

        lead_row = group_df.sort_values(["alert_prob_next_60m", "rank"], ascending=[False, True]).iloc[0]
        line_rows = (
            group_df[[
                "line",
                "alert_prob_next_60m",
                "delay_prob_next_60m",
                "suspension_prob_next_60m",
                "risk_index",
                "risk_level",
            ]]
            .sort_values(["alert_prob_next_60m", "line"], ascending=[False, True])
            .to_dict(orient="records")
        )
        cards.append(
            {
                "name": group["name"],
                "family": group["family"],
                "description": group["description"],
                "color": group["color"],
                "text_color": _line_label_text_color(group["color"]),
                "lines": group["lines"],
                "present_lines": group_df["line"].astype(str).tolist(),
                "risk_index": float(group_df["risk_index"].max()),
                "alert_prob_next_60m": float(group_df["alert_prob_next_60m"].max()),
                "delay_prob_next_60m": float(group_df["delay_prob_next_60m"].max()),
                "suspension_prob_next_60m": float(group_df["suspension_prob_next_60m"].max()),
                "lead_line": str(lead_row["line"]),
                "risk_level": str(lead_row["risk_level"]),
                "line_rows": line_rows,
            }
        )

    return sorted(
        cards,
        key=lambda card: (card["alert_prob_next_60m"], card["risk_index"]),
        reverse=True,
    )


def get_metro_dashboard_context() -> dict:
    snapshot = _load_snapshot()
    metro_map_static_filename, metro_map_version = _ensure_metro_prediction_map_file(
        snapshot,
        strict=True,
    )

    if snapshot is None:
        return {
            "available": False,
            "generation_command": "uv run python src/modelos/modelo_subway_produccion.py",
            "metro_map_static_filename": metro_map_static_filename,
            "metro_map_version": metro_map_version,
        }
        
    ### MINIO
    metrics = _read_json(METRICS_PATH_MINIO, {})
    importance = _read_json(IMPORTANCE_PATH_MINIO, [])

    ### LOCAL
    # metrics = _read_json(METRICS_PATH_LOCAL, [])
    # importance = _read_json(IMPORTANCE_PATH_LOCAL, [])

    top_line = snapshot.iloc[0].to_dict() if not snapshot.empty else None
    line_group_cards = _build_line_group_cards(snapshot)

    metric_cards = []
    for target, label in [
        ("alert_next_60m", "Alerta"),
        ("delay_next_60m", "Delay"),
        ("suspension_next_60m", "Suspension"),
    ]:
        target_metrics = metrics.get(target)
        if not target_metrics:
            continue

        metric_cards.append(
            {
                "label": label,
                "roc_auc": target_metrics.get("roc_auc"),
                "brier_score": target_metrics.get("brier_score"),
                "positive_rate": target_metrics.get("positive_rate"),
            }
        )

    snapshot_generated_from_hour = None
    prediction_window_start = None
    prediction_window_end = None

    if not snapshot.empty:
        snapshot_generated_from_hour = _format_datetime(snapshot.iloc[0]["snapshot_generated_from_hour"])
        prediction_window_start = _format_datetime(snapshot.iloc[0]["prediction_window_start"])
        prediction_window_end = _format_datetime(snapshot.iloc[0]["prediction_window_end"])

    return {
        "available": True,
        "top_line": top_line,
        "line_group_cards": line_group_cards,
        "metric_cards": metric_cards,
        "importance": importance[:8],
        "snapshot_generated_from_hour": snapshot_generated_from_hour,
        "prediction_window_start": prediction_window_start,
        "prediction_window_end": prediction_window_end,
        "meta": metrics.get("_meta", {}),
        "metro_map_static_filename": metro_map_static_filename,
        "metro_map_version": metro_map_version,
    }
