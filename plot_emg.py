#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import argparse
from matplotlib import cm
from matplotlib.colors import Normalize

def plot_emg_trace(
    csv_file,
    recording_index=0,
    channel_index=1,
    overlay=False,
    stim_col='stimulus_V',
    cmap_name='viridis',
    cmin=None,
    cmax=None,
    show_colorbar=False,
    color='gold',
    linewidth=1.5,
    figsize=(10, 4),
    dpi=300,
    tmin=None,
    tmax=None,
    hide_axes=True,
    transparent=True,
    output_file=None
):
    """
    If overlay==False:
        plots one trace like before.
    If overlay==True:
        pulls *all* recording_index for the given channel_index,
        colors them by stim_col using cmap_name, and overlays them.
    """
    df = pd.read_csv(csv_file)
    # apply channel filter
    df = df[df['channel_index'] == channel_index]
    # apply time window
    if tmin is not None:
        df = df[df['time_point'] >= tmin]
    if tmax is not None:
        df = df[df['time_point'] <= tmax]

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    if overlay:
        # pick out stimulus values
        stim_vals = df[stim_col].unique()
        vmin = cmin if cmin is not None else stim_vals.min()
        vmax = cmax if cmax is not None else stim_vals.max()
        norm = Normalize(vmin=vmin, vmax=vmax)
        cmap = cm.get_cmap(cmap_name)

        # iterate group by recording_index (or by stimulus if you like)
        for rec_idx, sub in df.groupby('recording_index', sort=True):
            stim = sub[stim_col].iloc[0]
            col = cmap(norm(stim))
            ax.plot(
                sub['time_point'],
                sub['amplitude_mV'],
                color=col,
                linewidth=linewidth
            )

        if show_colorbar:
            sm = cm.ScalarMappable(norm=norm, cmap=cmap)
            sm.set_array([])
            cbar = fig.colorbar(sm, ax=ax, pad=0.02)
            cbar.set_label(stim_col)

    else:
        # single‐trace mode
        sel = df[df['recording_index'] == recording_index]
        ax.plot(
            sel['time_point'],
            sel['amplitude_mV'],
            color=color,
            linewidth=linewidth
        )

    # enforce x‐limits if cropping
    if tmin is not None or tmax is not None:
        ax.set_xlim(tmin, tmax)

    if hide_axes:
        ax.axis('off')

    if output_file:
        fig.savefig(
            output_file,
            bbox_inches='tight',
            pad_inches=0,
            transparent=transparent
        )
        plt.close(fig)
        print(f"Saved EMG trace to {output_file}")
    else:
        plt.show()


if __name__ == '__main__':
    p = argparse.ArgumentParser(
        description="Plot one or all EMG traces colored by stimulus"
    )
    p.add_argument('csv_file', help='Path to your EMG CSV')
    p.add_argument('-r', '--recording', type=int, default=0,
                   help='recording_index to plot (ignored with --overlay)')
    p.add_argument('-c', '--channel', type=int, default=1,
                   help='channel_index to plot')
    p.add_argument('--overlay', action='store_true',
                   help='plot *all* recordings overlayed, colored by stimulus')
    p.add_argument('--stim-col',    type=str, default='stimulus_V',
                   help='column name for stimulus intensity')
    p.add_argument('--cmap',        type=str, default='viridis',
                   help='matplotlib colormap name (for overlay)')
    p.add_argument('--cmin',        type=float, default=None,
                   help='min stimulus for colormap normalization')
    p.add_argument('--cmax',        type=float, default=None,
                   help='max stimulus for colormap normalization')
    p.add_argument('--show-colorbar', action='store_true',
                   help='draw a colorbar when using --overlay')
    p.add_argument('--color',       type=str, default='gold',
                   help='trace color (for single‐trace mode)')
    p.add_argument('--linewidth',   type=float, default=1.5,
                   help='trace line width')
    p.add_argument('--figsize',     nargs=2, type=float, default=[10, 4],
                   help='figure size in inches: width height')
    p.add_argument('--dpi',         type=int, default=300,
                   help='figure resolution')
    p.add_argument('--tmin',        type=float, default=None,
                   help='start time (inclusive) to plot')
    p.add_argument('--tmax',        type=float, default=None,
                   help='end time (inclusive) to plot')
    p.add_argument('--no-hide-axes', action='store_true',
                   help='show axes/ticks')
    p.add_argument('--no-transparent', action='store_true',
                   help='save with opaque background')
    p.add_argument('-o', '--output', type=str,
                   help='output image file (e.g. overlay.png)')
    args = p.parse_args()

    plot_emg_trace(
        args.csv_file,
        recording_index=args.recording,
        channel_index=args.channel,
        overlay=args.overlay,
        stim_col=args.stim_col,
        cmap_name=args.cmap,
        cmin=args.cmin,
        cmax=args.cmax,
        show_colorbar=args.show_colorbar,
        color=args.color,
        linewidth=args.linewidth,
        figsize=tuple(args.figsize),
        dpi=args.dpi,
        tmin=args.tmin,
        tmax=args.tmax,
        hide_axes=not args.no_hide_axes,
        transparent=not args.no_transparent,
        output_file=args.output
    )
