#!/usr/bin/env python3
"""
Test script to demonstrate the new scale bar functionality
"""

import pandas as pd
import numpy as np
from plot_emg import plot_emg_trace

# Create some sample data for testing
def create_test_data():
    """Create a simple test CSV file with EMG-like data"""
    np.random.seed(42)
    
    # Parameters
    n_recordings = 3
    n_channels = 2
    n_timepoints = 1000
    
    data = []
    
    for recording in range(n_recordings):
        for channel in range(1, n_channels + 1):
            # Create time points
            time_points = np.linspace(-20, 80, n_timepoints)
            
            # Create synthetic EMG signal
            # Start with noise
            signal = np.random.normal(0, 5, n_timepoints)
            
            # Add a compound action potential around t=0
            t_peak = 0
            amplitude = 50 + recording * 20  # Different amplitudes for different recordings
            width = 2
            
            # Biphasic pulse
            pulse = amplitude * np.exp(-((time_points - t_peak) / width) ** 2)
            pulse -= 0.3 * amplitude * np.exp(-((time_points - t_peak - 1) / (width * 1.5)) ** 2)
            
            signal += pulse
            
            # Add stimulus information
            stimulus_voltage = 1.0 + recording * 0.5
            
            for i, (time, amp) in enumerate(zip(time_points, signal)):
                data.append({
                    'recording_index': recording,
                    'channel_index': channel,
                    'time_point': time,
                    'amplitude_mV': amp,
                    'stimulus_V': stimulus_voltage
                })
    
    df = pd.DataFrame(data)
    df.to_csv('test_emg_data.csv', index=False)
    print("Created test_emg_data.csv")
    return 'test_emg_data.csv'

def test_scale_bar_options():
    """Test the different scale bar options"""
    csv_file = create_test_data()
    
    print("Testing different scale bar configurations:")
    
    # Test 1: No scale bars (original behavior)
    print("1. No scale bars (original behavior)")
    plot_emg_trace(
        csv_file,
        recording_index=0,
        channel_index=1,
        output_file='test_results/test_no_bars.png',
        create_axes=False,
        plot_axes_on_trace=False
    )
    
    # Test 2: Only separate axes SVG (current default behavior)
    print("2. Only separate axes SVG")
    plot_emg_trace(
        csv_file,
        recording_index=0,
        channel_index=1,
        output_file='test_results/test_separate_axes.png',
        create_axes=True,
        plot_axes_on_trace=False
    )
    
    # Test 3: Only scale bars on trace (new feature)
    print("3. Only scale bars on trace")
    plot_emg_trace(
        csv_file,
        recording_index=0,
        channel_index=1,
        output_file='test_results/test_bars_on_trace.png',
        create_axes=False,
        plot_axes_on_trace=True
    )
    
    # Test 4: Both scale bars on trace AND separate axes SVG
    print("4. Both scale bars on trace AND separate axes SVG")
    plot_emg_trace(
        csv_file,
        recording_index=0,
        channel_index=1,
        output_file='test_results/test_both_axes.png',
        create_axes=True,
        plot_axes_on_trace=True
    )
    
    # Test 5: Overlay mode with scale bars on trace
    print("5. Overlay mode with scale bars on trace")
    plot_emg_trace(
        csv_file,
        channel_index=1,
        overlay=True,
        output_file='test_results/test_overlay_with_bars.png',
        create_axes=False,
        plot_axes_on_trace=True,
        show_colorbar=True
    )
    
    print("\nTest completed! Check the generated files:")
    print("- test_no_bars.png")
    print("- test_separate_axes.png + test_separate_axes_axes.svg")
    print("- test_bars_on_trace.png")
    print("- test_both_axes.png + test_both_axes_axes.svg")
    print("- test_overlay_with_bars.png")

if __name__ == '__main__':
    test_scale_bar_options()
