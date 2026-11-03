#!/usr/bin/env python3
"""Export the 1.1 V single-recording LG and TA traces as individual SVGs.

The example CSVs store integer channel IDs rather than muscle names. The
defaults match this dataset (LG: channel 0, TA: channel 1); both can be
overridden from the command line.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "Example project recordings" / "vibes"
REQUIRED_COLUMNS = {"channel_index", "stimulus_V", "time_point", "amplitude_mV"}


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




def load_trace(csv_path: Path, channel: int) -> tuple[pd.Series, pd.Series]:
    """Load and validate one channel from a single-recording CSV."""
    frame = pd.read_csv(csv_path)
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(
            f"{csv_path.name} is missing columns: {', '.join(sorted(missing))}"
        )

    channel_frame = frame.loc[frame["channel_index"] == channel].copy()
    if channel_frame.empty:
        available = sorted(frame["channel_index"].dropna().unique().tolist())
        raise ValueError(
            f"Channel {channel} is absent from {csv_path.name}; available channels: {available}"
        )

    stimulus_values = channel_frame["stimulus_V"].dropna().unique()
    if len(stimulus_values) != 1 or abs(float(stimulus_values[0]) - 1.1) > 1e-9:
        raise ValueError(
            f"Expected one 1.1 V trace in {csv_path.name}, channel {channel}; "
            f"found stimulus values {stimulus_values.tolist()}"
        )

    channel_frame = channel_frame.sort_values("time_point")
    if (
        channel_frame["time_point"].isna().any()
        or channel_frame["amplitude_mV"].isna().any()
    ):
        raise ValueError(
            f"Non-numeric or missing trace values in {csv_path.name}, channel {channel}"
        )
    if channel_frame["time_point"].duplicated().any():
        raise ValueError(f"Duplicate time points in {csv_path.name}, channel {channel}")

    return channel_frame["time_point"], channel_frame["amplitude_mV"]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export one 1.1 V SVG trace per mouse and channel from the vibes examples."
    )
    parser.add_argument(
        "--lg-channel",
        type=int,
        default=0,
        help="channel_index for LG (default: 0)",
    )
    parser.add_argument(
        "--ta-channel",
        type=int,
        default=1,
        help="channel_index for TA (default: 1)",
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
        default=DATA_DIR / "svg_1-1v",
        help="directory for the SVG files (default: data/Example project recordings/vibes/svg_1-1v)",
    )
    parser.add_argument(
        "--linewidth",
        type=float,
        default=0.8,
        help="trace width in points (default: 0.8)",
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

    csv_files = sorted(DATA_DIR.glob("1-1v_*_single.csv"))
    if not csv_files:
        raise FileNotFoundError(
            f"No 1-1v single-recording CSV files found in {DATA_DIR}"
        )

    channels = (
        ("LG", args.lg_channel),
        ("TA", args.ta_channel),
        ("Force", args.force_channel),
        ("Length", args.length_channel),
    )
    traces: dict[tuple[str, str], tuple[pd.Series, pd.Series]] = {}
    y_extents: dict[str, list[float]] = {
        muscle: [float("inf"), float("-inf")] for muscle, _ in channels
    }

    for csv_path in csv_files:
        mouse = csv_path.stem.removeprefix("1-1v_").removesuffix("_single")
        for muscle, channel in channels:
            time_ms, signal_values = load_trace(csv_path, channel)
            signal_values = scale_signal(signal_values, muscle)
            traces[(mouse, muscle)] = (time_ms, signal_values)
            y_extents[muscle][0] = min(y_extents[muscle][0], float(signal_values.min()))
            y_extents[muscle][1] = max(y_extents[muscle][1], float(signal_values.max()))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    plt.rcParams["svg.fonttype"] = "none"
    for (mouse, muscle), (time_ms, amplitude_mv) in traces.items():
        fig, ax = plt.subplots(figsize=(3.2, 1.45), layout="constrained")
        ax.plot(time_ms, amplitude_mv, color="black", linewidth=args.linewidth)
        ax.set_xlim(float(time_ms.min()), float(time_ms.max()))
        y_min, y_max = y_extents[muscle]
        padding = (y_max - y_min) * 0.05
        ax.set_ylim(y_min - padding, y_max + padding)
        ax.set_xlabel("Time (ms)")
        ax.set_ylabel(signal_ylabel(muscle))
        ax.set_title(f"{mouse} · {muscle} · 1.1 V", loc="left", fontsize=9)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(labelsize=7, width=0.6, length=2.5)
        for spine in (ax.spines["left"], ax.spines["bottom"]):
            spine.set_linewidth(0.6)

        output_path = args.output_dir / f"1-1v_{mouse}_{muscle}.svg"
        fig.savefig(output_path, format="svg", transparent=True)
        plt.close(fig)
        print(f"Saved {output_path}")

    print(
        f"Exported {len(traces)} SVGs for {len(csv_files)} mice. "
        "Each channel has its own y scale, shared across mice. Force is converted "
        "to mN and length to mm using the dissertation pipeline calibrations."
    )


if __name__ == "__main__":
    main()
