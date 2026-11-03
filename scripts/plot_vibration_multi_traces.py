#!/usr/bin/env python3
"""Export overlaid SVG plots for every repeated-trace vibration recording.

Each SVG shows all recordings for one mouse, stimulus intensity, and channel.
Each recording gets its own saturated color so overlapping traces remain visible.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "Example project recordings" / "vibes"
REQUIRED_COLUMNS = {
    "recording_index",
    "channel_index",
    "stimulus_V",
    "time_point",
    "amplitude_mV",
}


FORCE_MN_PER_VOLT = 102.5
LENGTH_MM_PER_VOLT = 1.36


def scale_signal(values: pd.Series, channel_name: str) -> pd.Series:
    """Convert exported force and length voltage samples to physical units."""
    if channel_name == "Force":
        return values * FORCE_MN_PER_VOLT
    if channel_name == "Length":
        return values * LENGTH_MM_PER_VOLT
    return values


def signal_ylabel(channel_name: str) -> str:
    """Return the display unit used for a channel."""
    if channel_name == "Force":
        return "Force (mN)"
    if channel_name == "Length":
        return "Length (mm)"
    return "Amplitude (mV)"


def read_multi_file(csv_path: Path) -> pd.DataFrame:
    """Read one multi-recording CSV and validate the columns and stimulus."""
    frame = pd.read_csv(csv_path)
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(
            f"{csv_path.name} is missing columns: {', '.join(sorted(missing))}"
        )

    stimulus_values = frame["stimulus_V"].dropna().unique()
    if len(stimulus_values) != 1:
        raise ValueError(
            f"Expected one stimulus intensity in {csv_path.name}; "
            f"found {stimulus_values.tolist()}"
        )
    return frame


def trace_colors(count: int) -> list[tuple[float, float, float, float]]:
    """Return distinct, saturated colors with enough contrast on white."""
    cmap = plt.get_cmap("hsv")
    hues = np.linspace(0.0, 1.0, count, endpoint=False)
    return [cmap(hue) for hue in hues]


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Export overlaid SVGs for each mouse and LG/TA, force, and length channels in the "
            "1-1v vibes multi-recording files."
        )
    )
    parser.add_argument(
        "--lg-channel", type=int, default=0, help="channel_index for LG (default: 0)"
    )
    parser.add_argument(
        "--ta-channel", type=int, default=1, help="channel_index for TA (default: 1)"
    )
    parser.add_argument(
        "--force-channel",
        type=int,
        default=2,
        help="channel_index for force (default: 2)",
    )
    parser.add_argument(
        "--length-channel",
        type=int,
        default=3,
        help="channel_index for length (default: 3)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DATA_DIR / "svg_multi",
        help="directory for SVG files (default: data/Example project recordings/vibes/svg_multi)",
    )
    parser.add_argument(
        "--linewidth", type=float, default=0.65, help="trace width in points (default: 0.65)"
    )
    args = parser.parse_args()

    selected_channels = [
        args.lg_channel,
        args.ta_channel,
        args.force_channel,
        args.length_channel,
    ]
    if len(set(selected_channels)) != len(selected_channels):
        parser.error("LG, TA, force, and length must use different channels")
    if args.linewidth <= 0:
        parser.error("--linewidth must be greater than zero")

    csv_files = sorted(DATA_DIR.glob("1-1v_*_multi.csv"))
    if not csv_files:
        raise FileNotFoundError(
            f"No 1-1v multi-recording CSV files found in {DATA_DIR}"
        )

    channels = (
        ("LG", args.lg_channel),
        ("TA", args.ta_channel),
        ("Force", args.force_channel),
        ("Length", args.length_channel),
    )

    # Establish one shared y range per channel across every mouse and stimulus.
    # Read one large CSV at a time to keep memory use bounded.
    y_extents = {
        muscle: [float("inf"), float("-inf")] for muscle, _ in channels
    }
    for csv_path in csv_files:
        frame = read_multi_file(csv_path)
        for muscle, channel in channels:
            amplitudes = scale_signal(
                frame.loc[frame["channel_index"] == channel, "amplitude_mV"].dropna(),
                muscle,
            )
            if amplitudes.empty:
                raise ValueError(
                    f"Channel {channel} ({muscle}) has no data in {csv_path.name}"
                )
            y_extents[muscle][0] = min(
                y_extents[muscle][0], float(amplitudes.min())
            )
            y_extents[muscle][1] = max(
                y_extents[muscle][1], float(amplitudes.max())
            )
        del frame

    args.output_dir.mkdir(parents=True, exist_ok=True)
    plt.rcParams["svg.fonttype"] = "none"
    plot_count = 0

    for csv_path in csv_files:
        frame = read_multi_file(csv_path)
        mouse = csv_path.stem.removesuffix("_multi").split("_", maxsplit=1)[1]
        stimulus = float(frame["stimulus_V"].iloc[0])

        for muscle, channel in channels:
            muscle_data = frame.loc[frame["channel_index"] == channel].copy()
            if muscle_data.empty:
                raise ValueError(
                    f"Channel {channel} ({muscle}) has no data in {csv_path.name}"
                )
            if muscle_data[["recording_index", "time_point", "amplitude_mV"]].isna().any().any():
                raise ValueError(f"Missing trace values in {csv_path.name}, channel {channel}")
            if muscle_data.duplicated(["recording_index", "time_point"]).any():
                raise ValueError(
                    f"Duplicate time points within a recording in {csv_path.name}, channel {channel}"
                )

            recording_ids = sorted(muscle_data["recording_index"].unique())
            colors = trace_colors(len(recording_ids))
            fig, ax = plt.subplots(figsize=(6.2, 3.4), layout="constrained")
            for recording_id, color in zip(recording_ids, colors):
                trace = muscle_data.loc[
                    muscle_data["recording_index"] == recording_id
                ].sort_values("time_point")
                ax.plot(
                    trace["time_point"],
                    scale_signal(trace["amplitude_mV"], muscle),
                    color=color,
                    linewidth=args.linewidth,
                    alpha=0.85,
                    rasterized=False,
                )

            ax.set_xlim(
                float(muscle_data["time_point"].min()),
                float(muscle_data["time_point"].max()),
            )
            y_min, y_max = y_extents[muscle]
            padding = (y_max - y_min) * 0.05
            ax.set_ylim(y_min - padding, y_max + padding)
            ax.set_xlabel("Time (ms)")
            ax.set_ylabel(signal_ylabel(muscle))
            ax.set_title(
                f"{mouse} · {muscle} · {stimulus:g} V · {len(recording_ids)} recordings",
                loc="left",
                fontsize=9,
            )
            ax.spines[["top", "right"]].set_visible(False)
            ax.tick_params(labelsize=7, width=0.6, length=2.5)
            for spine in (ax.spines["left"], ax.spines["bottom"]):
                spine.set_linewidth(0.6)

            stimulus_tag = f"{stimulus:g}v".replace(".", "-")
            output_path = args.output_dir / (
                f"{stimulus_tag}_{mouse}_{muscle}_multi.svg"
            )
            fig.savefig(
                output_path,
                format="svg",
                transparent=True,
            )
            plt.close(fig)
            plot_count += 1
            print(
                f"Saved {output_path} ({len(recording_ids)} individual traces)"
            )

        del frame

    print(
        f"Exported {plot_count} SVGs from {len(csv_files)} files. "
        "Each trace has a distinct color; each channel uses one shared y scale "
        "across all files. Force is in mN and length is in mm."
    )


if __name__ == "__main__":
    main()
