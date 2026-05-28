#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import argparse
from matplotlib import cm
from matplotlib.colors import Normalize
import os


def get_nice_scale_bar(data_span, target_fraction=0.25):
    """Return a readable scale-bar length based on a data span."""
    if data_span <= 0 or not isinstance(data_span, (int, float)) or data_span != data_span:
        return 1.0

    target_size = data_span * target_fraction

    if target_size >= 100:
        nice_values = [100, 200, 500]
    elif target_size >= 10:
        nice_values = [10, 20, 50]
    elif target_size >= 1:
        nice_values = [1, 2, 5]
    elif target_size >= 0.1:
        nice_values = [0.1, 0.2, 0.5]
    else:
        nice_values = [0.01, 0.02, 0.05]

    for val in nice_values:
        if val >= target_size * 0.5:
            return val
    return nice_values[-1]


def format_scale_value(value):
    """Format scale values without dropping useful precision."""
    if value >= 1:
        # Keep integers clean, otherwise preserve a compact decimal representation.
        return str(int(value)) if float(value).is_integer() else f"{value:g}"
    return f"{value:.3g}"

def create_axes_plot(
    output_file,
    x_range=None,
    y_range=None,
    x_label="Time (ms)",
    y_label="Amplitude (mV)",
    scale_bar_x=None,
    scale_bar_y=None,
    figsize=(4, 4),
    dpi=300,
    line_width=2.5,
    font_size=16
):
    """
    Create a clean axes plot with scale bars that represent the actual data scale.
    """
    # Set default ranges if not provided
    if x_range is None:
        x_range = (0, 100)
    if y_range is None:
        y_range = (-50, 50)
    
    # Calculate the actual data ranges
    x_span = x_range[1] - x_range[0]
    y_span = y_range[1] - y_range[0]

    if x_span <= 0 or y_span <= 0:
        raise ValueError("x_range and y_range must be increasing ranges")
    
    if scale_bar_x is None:
        scale_bar_x = get_nice_scale_bar(x_span)
    if scale_bar_y is None:
        scale_bar_y = get_nice_scale_bar(y_span)

    # Clamp bars so they always fit cleanly inside the visible ranges.
    scale_bar_x = min(scale_bar_x, x_span * 0.8)
    scale_bar_y = min(scale_bar_y, y_span * 0.8)
    
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    # Place bars in the lower-left with positive padding inside real data units.
    x_pad = x_span * 0.08
    y_pad = y_span * 0.08
    origin_x = x_range[0] + x_pad
    origin_y = y_range[0] + y_pad

    # End ticks sized as a fraction of plot spans.
    tick_size_x = x_span * 0.012
    tick_size_y = y_span * 0.012

    line_kwargs = dict(
        color='black',
        linewidth=line_width,
        antialiased=False,
        solid_capstyle='projecting',
        solid_joinstyle='miter',
    )

    # Draw feet first, then the main axis bars on top to avoid anti-aliased seams.
    ax.plot(
        [origin_x + scale_bar_x, origin_x + scale_bar_x],
        [origin_y - tick_size_y, origin_y + tick_size_y],
        **line_kwargs,
    )
    ax.plot(
        [origin_x - tick_size_x, origin_x + tick_size_x],
        [origin_y + scale_bar_y, origin_y + scale_bar_y],
        **line_kwargs,
    )

    # Main L-shaped bars in data coordinates.
    ax.plot(
        [origin_x, origin_x + scale_bar_x],
        [origin_y, origin_y],
        **line_kwargs,
    )
    ax.plot(
        [origin_x, origin_x],
        [origin_y, origin_y + scale_bar_y],
        **line_kwargs,
    )
    
    # Labels with proper formatting
    x_unit = x_label.split("(")[-1].rstrip(")") if "(" in x_label else ""
    y_unit = y_label.split("(")[-1].rstrip(")") if "(" in y_label else ""
    
    x_text = f"{format_scale_value(scale_bar_x)} {x_unit}".strip()
    y_text = f"{format_scale_value(scale_bar_y)} {y_unit}".strip()

    label_offset_x = x_span * 0.03
    label_offset_y = y_span * 0.03

    ax.text(
        origin_x + scale_bar_x / 2,
        origin_y - label_offset_y,
        x_text,
        ha='center',
        va='top',
        fontsize=font_size,
        color='black'
    )

    ax.text(
        origin_x - label_offset_x,
        origin_y + scale_bar_y / 2,
        y_text,
        ha='right',
        va='center',
        rotation=90,
        fontsize=font_size,
        color='black'
    )

    # Keep exported SVG coordinate system aligned to the source data ranges.
    ax.set_xlim(x_range)
    ax.set_ylim(y_range)
    
    # Clean appearance
    ax.axis('off')
    ax.set_facecolor('none')
    fig.patch.set_facecolor('none')
    
    # Save as SVG
    base_name, ext = os.path.splitext(output_file)
    axes_file = f"{base_name}_axes.svg"
    
    fig.savefig(
        axes_file,
        bbox_inches='tight',
        pad_inches=0.1,
        transparent=True,
        format='svg',
        facecolor='none'
    )
    plt.close(fig)
    print(f"Saved axes plot to {axes_file}")


def add_scale_bars_to_plot(
    ax,
    x_range=None,
    y_range=None,
    data_y_min=None,
    x_label="Time (ms)",
    y_label="Amplitude (mV)",
    scale_bar_x=None,
    scale_bar_y=None,
    position='bottom-right',
    line_width=2.0,
    font_size=12,
    color='black',
    place_outside_vertical=True,
):
    """
    Add scale bars directly to an existing plot.
    
    Parameters:
    -----------
    ax : matplotlib axes
        The axes to add scale bars to
    x_range, y_range : tuple
        (min, max) ranges for x and y axes
    data_y_min : float or None
        Minimum plotted-data y value used to place bars below the trace envelope.
    position : str
        Position of scale bars: 'bottom-right', 'bottom-left', 'top-right', 'top-left'
    place_outside_vertical : bool
        If True and a bottom position is used, place scale bars below the plotted
        data envelope and expand the lower y-limit as needed to avoid clipping.
    (Deprecated) offset_fraction : float
        Use fixed padding in axis fraction coordinates instead for consistent appearance
    """
    if x_range is None or y_range is None:
        # Get current axis limits
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        x_range = xlim if x_range is None else x_range
        y_range = ylim if y_range is None else y_range

    # Preserve current view so adding bars never recenters/reframes data.
    original_xlim = ax.get_xlim()
    original_ylim = ax.get_ylim()
    original_autoscale = ax.get_autoscale_on()

    # Calculate data ranges
    x_span = x_range[1] - x_range[0]
    y_span = y_range[1] - y_range[0]

    if x_span <= 0 or y_span <= 0:
        return

    if scale_bar_x is None:
        scale_bar_x = get_nice_scale_bar(x_span)
    if scale_bar_y is None:
        scale_bar_y = get_nice_scale_bar(y_span)

    # Ensure bars always fit inside visible limits.
    scale_bar_x = min(scale_bar_x, x_span * 0.8)
    scale_bar_y = min(scale_bar_y, y_span * 0.8)

    # Use positive inset padding so bars are always on-canvas.
    PAD_X = 0.06
    PAD_Y = 0.06

    # Convert axis fraction to data coordinates
    x_pad = PAD_X * x_span
    y_pad = PAD_Y * y_span

    if position == 'bottom-left':
        x_start = x_range[0] + x_pad
        y_start = y_range[0] + y_pad
    elif position == 'bottom-right':
        x_start = x_range[1] - x_pad - scale_bar_x
        y_start = y_range[0] + y_pad
    elif position == 'top-left':
        x_start = x_range[0] + x_pad
        y_start = y_range[1] - y_pad - scale_bar_y
    elif position == 'top-right':
        x_start = x_range[1] - x_pad - scale_bar_x
        y_start = y_range[1] - y_pad - scale_bar_y
    else:
        x_start = x_range[1] - x_pad - scale_bar_x
        y_start = y_range[0] + y_pad
    
    # Add tick marks at the ends
    tick_size_x = x_span * 0.01  # Small tick relative to x range
    tick_size_y = y_span * 0.01  # Small tick relative to y range

    # Move bottom-position scale bars below data traces to avoid overlap/clipping.
    keep_expanded_ylim = False
    if place_outside_vertical and position in ('bottom-left', 'bottom-right'):
        if data_y_min is None:
            detected_data_y_min = None
            for line in ax.lines:
                y_vals = line.get_ydata(orig=False)
                if y_vals is None or len(y_vals) == 0:
                    continue
                try:
                    line_min = min(y_vals)
                except Exception:
                    continue
                detected_data_y_min = line_min if detected_data_y_min is None else min(detected_data_y_min, line_min)

            data_y_min = detected_data_y_min if detected_data_y_min is not None else original_ylim[0]

        # Keep a clear visual gap between waveform and scale-axis block.
        gap_above_bar = max(y_span * 0.10, tick_size_y * 6)
        y_start = data_y_min - gap_above_bar - scale_bar_y

        # Reserve room for the bar + ticks + label below it.
        label_room = max(y_span * 0.10, tick_size_y * 10)
        needed_ymin = y_start - tick_size_y - label_room
        if needed_ymin < original_ylim[0]:
            ax.set_ylim(needed_ymin, original_ylim[1])
            keep_expanded_ylim = True
    
    line_kwargs = dict(
        color=color,
        linewidth=line_width,
        zorder=1000,
        antialiased=False,
        solid_capstyle='projecting',
        solid_joinstyle='miter',
        scalex=False,
        scaley=False,
    )

    # Draw feet first, then bars on top to prevent visible seams.
    # X-axis end tick
    ax.plot([x_start + scale_bar_x, x_start + scale_bar_x], 
            [y_start - tick_size_y, y_start + tick_size_y], 
            **line_kwargs)
    
    # Y-axis end tick  
    ax.plot([x_start - tick_size_x, x_start + tick_size_x], 
            [y_start + scale_bar_y, y_start + scale_bar_y], 
            **line_kwargs)

    # Horizontal bar (x-axis scale)
    ax.plot([x_start, x_start + scale_bar_x], [y_start, y_start], **line_kwargs)

    # Vertical bar (y-axis scale)
    ax.plot([x_start, x_start], [y_start, y_start + scale_bar_y], **line_kwargs)
    
    # Add labels
    x_unit = x_label.split("(")[-1].rstrip(")") if "(" in x_label else ""
    y_unit = y_label.split("(")[-1].rstrip(")") if "(" in y_label else ""

    x_text = f"{format_scale_value(scale_bar_x)} {x_unit}".strip()
    y_text = f"{format_scale_value(scale_bar_y)} {y_unit}".strip()
    
    # Position labels appropriately
    label_offset_x = tick_size_x * 3
    label_offset_y = tick_size_y * 3
    
    # X-axis label (below the horizontal bar)
    ax.text(x_start + scale_bar_x/2, y_start - label_offset_y, x_text, 
            ha='center', va='top', fontsize=font_size, color=color, zorder=1000)
    
    # Y-axis label (to the left of the vertical bar, rotated)
    ax.text(x_start - label_offset_x, y_start + scale_bar_y/2, y_text, 
            ha='right', va='center', rotation=90, fontsize=font_size, color=color, zorder=1000)

    # Restore limits/autoscale state in case backends update view from new artists.
    ax.set_xlim(original_xlim)
    if not keep_expanded_ylim:
        ax.set_ylim(original_ylim)
    ax.set_autoscale_on(original_autoscale)


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
    output_file=None,
    fixed_y=False,
    create_axes=False,
    plot_axes_on_trace=False,
    x_min=None,
    x_max=None,
    y_min=None,
    y_max=None
):
    """
    If overlay==False:
        plots one trace like before.
    If overlay==True:
        pulls *all* recording_index for the given channel_index,
        colors them by stim_col using cmap_name, and overlays them.
    
    Parameters:
    -----------
    fixed_y : bool, default=True
        If True, sets y-axis limits based on the full dataset for the channel.
        This ensures consistent y-axis scaling across different recordings.
        If False, y-axis auto-scales to the current data being plotted.
    create_axes : bool, default=True
        If True and output_file is specified, creates a separate SVG file
        with clean axes that can be used as a scalable graphic in CorelDraw.
    plot_axes_on_trace : bool, default=False
        If True, adds scale bars directly to the trace plot itself.
        Can be used together with create_axes for both on-plot and separate axes.
    x_min, x_max : float or None
        Manual x-axis limits. When either is provided, x-axis auto/fitted limits are
        overridden by the provided values.
    y_min, y_max : float or None
        Manual y-axis limits. When either is provided, y-axis auto/fixed_y limits are
        overridden by the provided values.
    """
    df = pd.read_csv(csv_file)
    # apply channel filter
    df = df[df['channel_index'] == channel_index]
    
    # Calculate global y-limits for fixed scaling if needed
    if fixed_y and not overlay:
        fixed_data_y_min = df['amplitude_mV'].min()
        fixed_data_y_max = df['amplitude_mV'].max()
        
        # Validate y-limits
        if pd.isna(fixed_data_y_min) or pd.isna(fixed_data_y_max) or fixed_data_y_min == fixed_data_y_max:
            fixed_y = False  # Disable fixed scaling if invalid
        else:
            # Add some padding (5% on each side)
            fixed_y_range = fixed_data_y_max - fixed_data_y_min
            y_padding = fixed_y_range * 0.05
            y_min_padded = fixed_data_y_min - y_padding
            y_max_padded = fixed_data_y_max + y_padding
    
    # apply time window
    if tmin is not None:
        df = df[df['time_point'] >= tmin]
    if tmax is not None:
        df = df[df['time_point'] <= tmax]

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    if overlay:
        # pick out stimulus values
        stim_vals = df[stim_col].unique()
        if len(stim_vals) != 0:
            vmin = cmin if cmin is not None else stim_vals.min()
            vmax = cmax if cmax is not None else stim_vals.max()
        elif len(stim_vals) == 1:
            vmin = vmax = stim_vals[0]
        else:
            vmin = 0
            vmax = 1
            
        norm = Normalize(vmin=vmin, vmax=vmax)
        cmap = plt.get_cmap(cmap_name)

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

    # Track actual plotted-data vertical extent for robust scale-bar placement.
    if overlay:
        plotted_data_y_min = df['amplitude_mV'].min()
    else:
        plotted_data_y_min = sel['amplitude_mV'].min()

    if pd.isna(plotted_data_y_min):
        plotted_data_y_min = ax.get_ylim()[0]

    # Apply x-axis limits: manual values take priority over time window limits.
    if x_min is not None or x_max is not None:
        current_xlim = ax.get_xlim()
        ax.set_xlim(
            x_min if x_min is not None else current_xlim[0],
            x_max if x_max is not None else current_xlim[1],
        )
    elif tmin is not None or tmax is not None:
        current_xlim = ax.get_xlim()
        ax.set_xlim(
            tmin if tmin is not None else current_xlim[0],
            tmax if tmax is not None else current_xlim[1],
        )

    # Apply y-axis limits: manual values take priority over fixed_y limits.
    if y_min is not None or y_max is not None:
        current_ylim = ax.get_ylim()
        ax.set_ylim(
            y_min if y_min is not None else current_ylim[0],
            y_max if y_max is not None else current_ylim[1],
        )
    elif fixed_y and not overlay:
        ax.set_ylim(y_min_padded, y_max_padded)

    if hide_axes:
        ax.axis('off')

    # Add scale bars to the plot if requested
    if plot_axes_on_trace:
        # Determine the appropriate ranges for the scale bars
        if y_min is not None or y_max is not None:
            ylim = ax.get_ylim()
            y_range = (ylim[0], ylim[1])
        elif fixed_y and not overlay:
            y_range = (y_min_padded, y_max_padded)
        else:
            # Use the current plot's y-limits
            ylim = ax.get_ylim()
            y_range = ylim
        
        # Use the final rendered x-limits so scale bars match manual/cropped axes.
        if x_min is not None or x_max is not None:
            xlim = ax.get_xlim()
            x_range = (xlim[0], xlim[1])
        elif tmin is not None and tmax is not None:
            x_range = (tmin, tmax)
        else:
            xlim = ax.get_xlim()
            x_range = xlim
        
        # Add scale bars to the plot
        add_scale_bars_to_plot(
            ax,
            x_range=x_range,
            y_range=y_range,
            data_y_min=plotted_data_y_min,
            x_label="Time (ms)",
            y_label="Amplitude (mV)",
            position='bottom-left',
            line_width=1.5,
            font_size=10,
            color='black'
        )

    if output_file:
        # Create dir if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        fig.savefig( # Save the plot to the specified output file
            output_file,
            bbox_inches='tight',
            pad_inches=0,
            transparent=transparent
        )
        plt.close(fig)
        print(f"Saved EMG trace to {output_file}")
        
        # Create axes plot if requested
        if create_axes:
            # Determine the appropriate ranges for the axes
            if y_min is not None or y_max is not None:
                ylim = ax.get_ylim()
                y_range = (ylim[0], ylim[1])
            elif fixed_y and not overlay:
                y_range = (y_min_padded, y_max_padded)
            else:
                # Use the current plot's y-limits
                current_y_min = sel['amplitude_mV'].min() if not overlay else df['amplitude_mV'].min()
                current_y_max = sel['amplitude_mV'].max() if not overlay else df['amplitude_mV'].max()
                y_range = (current_y_min, current_y_max)
            
            # Use final rendered x-limits so external axes match the trace plot.
            if x_min is not None or x_max is not None:
                xlim = ax.get_xlim()
                x_range = (xlim[0], xlim[1])
            elif tmin is not None and tmax is not None:
                x_range = (tmin, tmax)
            else:
                data_x_min = df['time_point'].min()
                data_x_max = df['time_point'].max()
                x_range = (data_x_min, data_x_max)
            
            create_axes_plot(
                output_file,
                x_range=x_range,
                y_range=y_range,
                x_label="Time (ms)",
                y_label="Amplitude (mV)"
            )
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
    p.add_argument('--no-fixed-y', action='store_true',
                   help='disable fixed y-axis scaling (auto-scale each plot)')
    p.add_argument('--no-axes', action='store_true',
                   help='disable creation of separate axes SVG file')
    p.add_argument('--plot-axes-on-trace', action='store_true',
                   help='add scale bars directly to the trace plot')
    p.add_argument('--x-min', type=float, default=None,
                   help='manual minimum x-axis value')
    p.add_argument('--x-max', type=float, default=None,
                   help='manual maximum x-axis value')
    p.add_argument('--y-min', type=float, default=None,
                   help='manual minimum y-axis value')
    p.add_argument('--y-max', type=float, default=None,
                   help='manual maximum y-axis value')
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
        output_file=args.output,
        fixed_y=not args.no_fixed_y,
        create_axes=not args.no_axes,
        plot_axes_on_trace=args.plot_axes_on_trace,
        x_min=args.x_min,
        x_max=args.x_max,
        y_min=args.y_min,
        y_max=args.y_max
    )
