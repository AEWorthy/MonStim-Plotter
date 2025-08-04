#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import argparse
from matplotlib import cm
from matplotlib.colors import Normalize
import os

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
    
    # Calculate sensible scale bar lengths (about 1/4 to 1/5 of the data range)
    def get_nice_scale_bar(data_span, target_fraction=0.25):
        """Get a nice round number for scale bars"""
        if data_span <= 0 or not isinstance(data_span, (int, float)) or data_span != data_span:  # Check for NaN/Inf
            return 1.0  # Default fallback
            
        target_size = data_span * target_fraction
        
        # Find the appropriate magnitude and choose nice values
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
        
        # Choose the best value
        for val in nice_values:
            if val >= target_size * 0.5:
                return val
        return nice_values[-1]
    
    if scale_bar_x is None:
        scale_bar_x = get_nice_scale_bar(x_span)
    if scale_bar_y is None:
        scale_bar_y = get_nice_scale_bar(y_span)
    
    # Set up the plot with clean settings
    plt.rcParams['font.family'] = 'Arial'
    plt.rcParams['font.size'] = font_size
    plt.rcParams['font.weight'] = 'normal'
    
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    
    # Create axes that are properly scaled to the data
    # The axes should represent the actual proportion of the scale bars to the data
    x_axis_length = (scale_bar_x / x_span) * 8  # 8 units for visual appeal
    y_axis_length = (scale_bar_y / y_span) * 8  # 8 units for visual appeal
    
    origin_x, origin_y = 0, 0
    
    # Main L-shaped axes - these represent the scale bars themselves
    ax.plot([origin_x, origin_x], [origin_y, y_axis_length], 
            'k-', linewidth=line_width, solid_capstyle='round')
    ax.plot([origin_x, x_axis_length], [origin_y, origin_y], 
            'k-', linewidth=line_width, solid_capstyle='round')
    
    # Add tick marks at the ends to show the scale
    tick_size = min(x_axis_length, y_axis_length) * 0.05
    
    # X-axis end tick
    ax.plot([x_axis_length, x_axis_length], [-tick_size, tick_size], 
            'k-', linewidth=line_width)
    
    # Y-axis end tick  
    ax.plot([-tick_size, tick_size], [y_axis_length, y_axis_length], 
            'k-', linewidth=line_width)
    
    # Labels with proper formatting
    x_unit = x_label.split("(")[-1].rstrip(")") if "(" in x_label else ""
    y_unit = y_label.split("(")[-1].rstrip(")") if "(" in y_label else ""
    
    # Format the scale bar values appropriately
    if scale_bar_x >= 1:
        x_text = f"{int(scale_bar_x)} {x_unit}".strip()
    else:
        x_text = f"{scale_bar_x:.2f} {x_unit}".strip()
    
    if scale_bar_y >= 1:
        y_text = f"{int(scale_bar_y)} {y_unit}".strip()
    else:
        y_text = f"{scale_bar_y:.2f} {y_unit}".strip()
    
    # Position labels clearly
    ax.text(x_axis_length/2, -tick_size * 4, x_text, 
            ha='center', va='top', fontsize=font_size)
    
    ax.text(-tick_size * 4, y_axis_length/2, y_text, 
            ha='right', va='center', rotation=90, fontsize=font_size)
    
    # Set limits with appropriate padding
    padding = max(x_axis_length, y_axis_length) * 0.3
    
    ax.set_xlim(-padding, x_axis_length + padding * 0.5)
    ax.set_ylim(-padding, y_axis_length + padding * 0.5)
    
    # Make sure axes are equal so scale is preserved
    ax.set_aspect('equal')
    
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
    
    # Reset font settings
    plt.rcParams.update(plt.rcParamsDefault)

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
    create_axes=False
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
    """
    df = pd.read_csv(csv_file)
    # apply channel filter
    df = df[df['channel_index'] == channel_index]
    
    # Calculate global y-limits for fixed scaling if needed
    if fixed_y and not overlay:
        y_min = df['amplitude_mV'].min()
        y_max = df['amplitude_mV'].max()
        
        # Validate y-limits
        if pd.isna(y_min) or pd.isna(y_max) or y_min == y_max:
            fixed_y = False  # Disable fixed scaling if invalid
        else:
            # Add some padding (5% on each side)
            y_range = y_max - y_min
            y_padding = y_range * 0.05
            y_min_padded = y_min - y_padding
            y_max_padded = y_max + y_padding
    
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

    # enforce x‐limits if cropping
    if tmin is not None or tmax is not None:
        ax.set_xlim(tmin, tmax)
    
    # enforce y-limits for consistent scaling if fixed_y is True
    if fixed_y and not overlay:
        ax.set_ylim(y_min_padded, y_max_padded)

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
        
        # Create axes plot if requested
        if create_axes:
            # Determine the appropriate ranges for the axes
            if fixed_y and not overlay:
                y_range = (y_min_padded, y_max_padded)
            else:
                # Use the current plot's y-limits
                current_y_min = sel['amplitude_mV'].min() if not overlay else df['amplitude_mV'].min()
                current_y_max = sel['amplitude_mV'].max() if not overlay else df['amplitude_mV'].max()
                y_range = (current_y_min, current_y_max)
            
            # Use time window if specified, otherwise use data range
            if tmin is not None and tmax is not None:
                x_range = (tmin, tmax)
            else:
                x_min = df['time_point'].min()
                x_max = df['time_point'].max()
                x_range = (x_min, x_max)
            
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
        create_axes=not args.no_axes
    )
