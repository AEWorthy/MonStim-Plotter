#!/usr/bin/env python3
"""
Example usage of the EMG Plotting tools - both command line and GUI
This script demonstrates various ways to use the plotting functionality.
"""

import os
import subprocess
from plot_emg import plot_emg_trace

def example_command_line_usage():
    """Examples of using the command-line interface"""
    print("=" * 60)
    print("COMMAND LINE EXAMPLES")
    print("=" * 60)
    
    # Make sure we have a sample CSV file
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    if not csv_files:
        print("No CSV files found for examples")
        return
    
    sample_csv = csv_files[0]
    print(f"Using sample file: {sample_csv}")
    print()
    
    # Example 1: Basic single trace plot
    print("Example 1: Single trace plot (preview)")
    try:
        plot_emg_trace(
            csv_file=sample_csv,
            recording_index=0,
            channel_index=1,
            color='red',
            linewidth=2.0,
            output_file=None  # Preview mode
        )
        print("✓ Single trace preview completed")
    except Exception as e:
        print(f"✗ Error: {e}")
    print()
    
    # Example 2: Overlay plot with all recordings
    print("Example 2: Overlay plot (all recordings)")
    try:
        plot_emg_trace(
            csv_file=sample_csv,
            channel_index=1,
            overlay=True,
            cmap_name='inferno',
            show_colorbar=True,
            output_file='example_overlay.png',
            figsize=(12, 6),
            dpi=300
        )
        print("✓ Overlay plot saved as example_overlay.png")
    except Exception as e:
        print(f"✗ Error: {e}")
    print()
    
    # Example 3: Cropped time window
    print("Example 3: Cropped time window")
    try:
        plot_emg_trace(
            csv_file=sample_csv,
            recording_index=5,
            channel_index=1,
            tmin=-5,
            tmax=60,
            color='blue',
            output_file='example_cropped.png',
            create_axes=True
        )
        print("✓ Cropped plot saved as example_cropped.png")
        print("✓ Axes file saved as example_cropped_axes.svg")
    except Exception as e:
        print(f"✗ Error: {e}")
    print()

def example_programmatic_usage():
    """Examples of using the functions programmatically"""
    print("=" * 60)
    print("PROGRAMMATIC EXAMPLES")
    print("=" * 60)
    
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    if not csv_files:
        print("No CSV files found for examples")
        return
    
    sample_csv = csv_files[0]
    
    # Example: Batch processing multiple recordings
    print("Example: Batch processing multiple recordings")
    try:
        import pandas as pd
        
        # Read CSV to see what recordings are available
        df = pd.read_csv(sample_csv)
        available_recordings = sorted(df['recording_index'].unique())
        
        print(f"Found {len(available_recordings)} recordings: {available_recordings[:10]}...")
        
        # Create plots for first few recordings
        for i, rec_idx in enumerate(available_recordings[:3]):
            output_file = f"batch_recording_{rec_idx:03d}.png"
            
            plot_emg_trace(
                csv_file=sample_csv,
                recording_index=rec_idx,
                channel_index=1,
                color='green',
                linewidth=1.5,
                output_file=output_file,
                hide_axes=True,
                transparent=True
            )
            print(f"✓ Created {output_file}")
        
        print("✓ Batch processing completed")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    print()

def example_gui_launch():
    """Example of launching the GUI"""
    print("=" * 60)
    print("GUI EXAMPLES")
    print("=" * 60)
    
    print("You can launch the GUI in several ways:")
    print()
    print("1. Direct Python execution:")
    print("   python emg_plotter_gui.py")
    print()
    print("2. Using the batch file (Windows):")
    print("   run_gui.bat")
    print()
    print("3. Using the shell script (Mac/Linux):")
    print("   ./run_gui.sh")
    print()
    print("4. Using the demo script:")
    print("   python demo_gui.py")
    print()
    print("5. Programmatically:")
    print("   from emg_plotter_gui import main")
    print("   main()")
    print()

def show_command_line_help():
    """Show command line help"""
    print("=" * 60)
    print("COMMAND LINE OPTIONS")
    print("=" * 60)
    
    try:
        result = subprocess.run(['python', 'plot_emg.py', '--help'], 
                              capture_output=True, text=True)
        print(result.stdout)
    except Exception as e:
        print(f"Could not show help: {e}")

def main():
    """Main example function"""
    print("EMG Plotter Usage Examples")
    print("=" * 60)
    
    # Check if we have data files
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    print(f"Found {len(csv_files)} CSV files in current directory")
    
    if csv_files:
        print("Available CSV files:")
        for i, csv_file in enumerate(csv_files[:5]):
            print(f"  {i+1}. {csv_file}")
        if len(csv_files) > 5:
            print(f"  ... and {len(csv_files) - 5} more")
    else:
        print("No CSV files found. Examples will show syntax only.")
    
    print()
    
    # Show different usage examples
    example_command_line_usage()
    example_programmatic_usage()
    example_gui_launch()
    show_command_line_help()
    
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("✓ Command line: Use plot_emg.py directly")
    print("✓ Programmatic: Import and use plot_emg_trace() function")
    print("✓ GUI: Run emg_plotter_gui.py for interactive plotting")
    print("✓ Batch processing: Loop over recordings/channels")
    print("✓ Multiple formats: PNG, SVG, PDF output supported")
    print("✓ Scalable graphics: Auto-generated axes SVG files")

if __name__ == '__main__':
    main()
