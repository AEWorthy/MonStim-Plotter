#!/usr/bin/env python3
"""
EMG Plotter GUI - A lightweight PyQt6 application for plotting EMG traces
Author: Andrew Worthy
Based on the plot_emg.py script
"""

import sys
import os

# Set matplotlib backend before importing PyQt6 to avoid conflicts
import matplotlib
# Ensure we have a GUI backend that works with PyQt6
matplotlib.use('Qt5Agg')

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QFormLayout, QGroupBox, QPushButton, QLabel, QLineEdit, QFileDialog, 
    QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox, QTextEdit, QMessageBox,
    QProgressBar, QTabWidget, QFrame, QColorDialog
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont, QIcon, QColor

# Import the plotting functions from our existing script
from plot_emg import plot_emg_trace

import pandas as pd


class PlottingWorker(QThread):
    """Worker thread for plotting operations to prevent GUI freezing"""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, plot_function, **kwargs):
        super().__init__()
        self.plot_function = plot_function
        self.kwargs = kwargs

    def run(self):
        try:
            self.progress.emit("Starting plot generation...")
            # Ensure we're only saving to file in worker thread (no GUI display)
            if self.kwargs.get('output_file') is None:
                self.error.emit("Worker thread should only be used for saving to file")
                return
            
            self.plot_function(**self.kwargs)
            self.progress.emit("Plot generation completed!")
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class FileSelectionWidget(QGroupBox):
    """Widget for file selection and basic file info"""
    
    def __init__(self):
        super().__init__("File Selection")
        self.csv_file = None
        self.available_recordings = []
        self.available_channels = []
        self.file_info_callback = None  # Callback for when file info is updated
        self.setup_ui()
        
    def set_file_info_callback(self, callback):
        """Set callback function to be called when file info is updated"""
        self.file_info_callback = callback
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # File selection row
        file_row = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("QLabel { color: palette(disabled-text); font-style: italic; }")
        self.browse_button = QPushButton("Browse CSV File...")
        self.browse_button.clicked.connect(self.browse_file)
        
        file_row.addWidget(self.file_label, 1)
        file_row.addWidget(self.browse_button)
        layout.addLayout(file_row)
        
        # File info
        self.info_text = QTextEdit()
        self.info_text.setMaximumHeight(100)
        self.info_text.setReadOnly(True)
        # Use system colors for better dark mode compatibility
        self.info_text.setStyleSheet("QTextEdit { background-color: palette(base); }")
        # Add some default text to test if the widget is working
        self.info_text.setText("File info will appear here when you select a CSV file...")
        layout.addWidget(self.info_text)
        
        self.setLayout(layout)
    
    def browse_file(self):
        """Open file dialog to select CSV file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select EMG CSV File", 
            "", 
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            self.csv_file = file_path
            filename = os.path.basename(file_path)
            self.file_label.setText(filename)
            # Use system colors that adapt to dark/light themes
            self.file_label.setStyleSheet("QLabel { font-weight: bold; }")
            self.load_file_info()
    
    def load_file_info(self):
        """Load and display basic file information"""
        if not self.csv_file:
            return
            
        try:
            # Read just the first few rows to get info
            df = pd.read_csv(self.csv_file, nrows=1000)
            
            # Store available recordings and channels
            if 'recording_index' in df.columns:
                self.available_recordings = sorted(df['recording_index'].unique())
            else:
                self.available_recordings = []
                
            if 'channel_index' in df.columns:
                self.available_channels = sorted(df['channel_index'].unique())
            else:
                self.available_channels = []
            
            info_text = f"File: {os.path.basename(self.csv_file)}\n"
            info_text += f"Columns: {', '.join(df.columns.tolist())}\n"
            
            if 'recording_index' in df.columns:
                recordings = df['recording_index'].nunique()
                info_text += f"Number of recordings: {recordings}\n"
            
            if 'channel_index' in df.columns:
                channels = sorted(df['channel_index'].unique())
                info_text += f"Available channels: {channels}\n"
            
            if 'stimulus_V' in df.columns:
                stim_range = f"{df['stimulus_V'].min():.2f} - {df['stimulus_V'].max():.2f} V"
                info_text += f"Stimulus range: {stim_range}\n"
            
            if 'time_point' in df.columns:
                time_range = f"{df['time_point'].min():.1f} - {df['time_point'].max():.1f} ms"
                info_text += f"Time range: {time_range}"
            
            # Set the text and force update
            self.info_text.clear()
            self.info_text.setText(info_text)
            self.info_text.update()
            
            # Call callback if set
            if self.file_info_callback:
                self.file_info_callback(self.available_recordings, self.available_channels)
            
        except Exception as e:
            error_msg = f"Error reading file: {str(e)}"
            self.info_text.setText(error_msg)
            self.available_recordings = []
            self.available_channels = []


class PlotOptionsWidget(QGroupBox):
    """Widget for plot configuration options"""
    
    def __init__(self):
        super().__init__("Plot Options")
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Create tabs for different option groups
        tab_widget = QTabWidget()
        
        # Basic options tab
        basic_tab = QWidget()
        basic_layout = QFormLayout()
        
        # Recording and channel selectors (will be populated when file is loaded)
        self.recording_combo = QComboBox()
        self.recording_combo.setToolTip("Select which recording index to plot from the CSV file")
        basic_layout.addRow("Recording Index:", self.recording_combo)
        
        self.channel_combo = QComboBox()
        self.channel_combo.setToolTip("Select which channel index to plot from the CSV file")
        basic_layout.addRow("Channel Index:", self.channel_combo)
        
        self.overlay_check = QCheckBox()
        self.overlay_check.toggled.connect(self.on_overlay_toggled)
        self.overlay_check.setToolTip("When enabled, overlays all recordings on the same plot with color coding")
        basic_layout.addRow("Overlay All Recordings:", self.overlay_check)
        
        # Color picker for single trace
        color_row = QHBoxLayout()
        self.color_edit = QLineEdit("#ffd700")
        self.color_edit.setToolTip("Color name or hex code for single trace plots (e.g., 'gold', '#FFD700')")
        
        # Color swatch to show current color
        self.color_swatch = QLabel()
        self.color_swatch.setFixedSize(30, 23)  # Match height with line edit
        self.color_swatch.setStyleSheet("QLabel { border: 1px solid gray; }")
        self.color_swatch.setToolTip("Current selected color")
        
        self.color_button = QPushButton("Pick Color")
        self.color_button.clicked.connect(self.pick_color)
        self.color_button.setToolTip("Open color picker dialog")
        
        # Connect text changes to update swatch
        self.color_edit.textChanged.connect(self.update_color_swatch)
        
        color_row.addWidget(self.color_edit, 1)
        color_row.addWidget(self.color_swatch)
        color_row.addWidget(self.color_button)
        basic_layout.addRow("Single Trace Color:", color_row)
        
        # Initialize color swatch
        self.update_color_swatch()
        
        basic_tab.setLayout(basic_layout)
        tab_widget.addTab(basic_tab, "Basic")
        
        # Overlay options tab
        overlay_tab = QWidget()
        overlay_layout = QFormLayout()
        
        self.stim_col_edit = QLineEdit("stimulus_V")
        self.stim_col_edit.setToolTip("Name of the column containing stimulus values for color coding")
        overlay_layout.addRow("Stimulus Column:", self.stim_col_edit)
        
        self.cmap_combo = QComboBox()
        self.cmap_combo.addItems([
            'viridis', 'plasma', 'inferno', 'magma', 'inferno_r',
            'cool', 'hot', 'spring', 'summer', 'autumn', 'winter'
        ])
        self.cmap_combo.setToolTip("Colormap to use for color coding overlaid traces")
        overlay_layout.addRow("Colormap:", self.cmap_combo)
        
        self.cmin_spin = QDoubleSpinBox()
        self.cmin_spin.setMinimum(-999.99)
        self.cmin_spin.setMaximum(999.99)
        self.cmin_spin.setSpecialValueText("Auto")
        self.cmin_spin.setValue(-999.99)
        self.cmin_spin.setToolTip("Minimum stimulus value for color scale (Auto = use data minimum)")
        overlay_layout.addRow("Color Min (V):", self.cmin_spin)
        
        self.cmax_spin = QDoubleSpinBox()
        self.cmax_spin.setMinimum(-999.99)
        self.cmax_spin.setMaximum(999.99)
        self.cmax_spin.setSpecialValueText("Auto")
        self.cmax_spin.setValue(-999.99)
        self.cmax_spin.setToolTip("Maximum stimulus value for color scale (Auto = use data maximum)")
        overlay_layout.addRow("Color Max (V):", self.cmax_spin)
        
        self.colorbar_check = QCheckBox()
        self.colorbar_check.setToolTip("Display a colorbar showing the stimulus-to-color mapping")
        self.colorbar_check.setChecked(True)
        overlay_layout.addRow("Show Colorbar:", self.colorbar_check)
        
        overlay_tab.setLayout(overlay_layout)
        tab_widget.addTab(overlay_tab, "Overlay")
        
        # Appearance options tab
        appearance_tab = QWidget()
        appearance_layout = QFormLayout()
        
        self.linewidth_spin = QDoubleSpinBox()
        self.linewidth_spin.setMinimum(0.1)
        self.linewidth_spin.setMaximum(10.0)
        self.linewidth_spin.setSingleStep(0.1)
        self.linewidth_spin.setValue(1.5)
        self.linewidth_spin.setToolTip("Width of the plotted trace lines")
        appearance_layout.addRow("Line Width:", self.linewidth_spin)
        
        self.figsize_width = QDoubleSpinBox()
        self.figsize_width.setMinimum(1.0)
        self.figsize_width.setMaximum(20.0)
        self.figsize_width.setValue(4.0)
        self.figsize_width.setToolTip("Width of the output figure in inches")
        appearance_layout.addRow("Figure Width (inches):", self.figsize_width)
        
        self.figsize_height = QDoubleSpinBox()
        self.figsize_height.setMinimum(1.0)
        self.figsize_height.setMaximum(20.0)
        self.figsize_height.setValue(2.0)
        self.figsize_height.setToolTip("Height of the output figure in inches")
        appearance_layout.addRow("Figure Height (inches):", self.figsize_height)
        
        self.dpi_spin = QSpinBox()
        self.dpi_spin.setMinimum(50)
        self.dpi_spin.setMaximum(600)
        self.dpi_spin.setValue(300)
        self.dpi_spin.setToolTip("Resolution of the output figure (dots per inch)")
        appearance_layout.addRow("DPI:", self.dpi_spin)
        
        self.hide_axes_check = QCheckBox()
        self.hide_axes_check.setChecked(True)
        self.hide_axes_check.setToolTip("Hide matplotlib plot axes, labels, and ticks for clean trace display")
        appearance_layout.addRow("Hide Default Plot Axes:", self.hide_axes_check)
        
        self.transparent_check = QCheckBox()
        self.transparent_check.setChecked(True)
        self.transparent_check.setToolTip("Use transparent background for the plot")
        appearance_layout.addRow("Transparent Background:", self.transparent_check)
        
        appearance_tab.setLayout(appearance_layout)
        tab_widget.addTab(appearance_tab, "Appearance")
        
        # Time window tab
        time_tab = QWidget()
        time_layout = QFormLayout()
        
        self.tmin_spin = QDoubleSpinBox()
        self.tmin_spin.setMinimum(-9999.99)
        self.tmin_spin.setMaximum(9999.99)
        self.tmin_spin.setSpecialValueText("Auto")
        self.tmin_spin.setValue(-9999.99)
        self.tmin_spin.setToolTip("Minimum time value to display (Auto = use data minimum)")
        time_layout.addRow("Time Min (ms):", self.tmin_spin)
        
        self.tmax_spin = QDoubleSpinBox()
        self.tmax_spin.setMinimum(-9999.99)
        self.tmax_spin.setMaximum(9999.99)
        self.tmax_spin.setSpecialValueText("Auto")
        self.tmax_spin.setValue(-9999.99)
        self.tmax_spin.setToolTip("Maximum time value to display (Auto = use data maximum)")
        time_layout.addRow("Time Max (ms):", self.tmax_spin)
        
        self.fixed_y_check = QCheckBox()
        self.fixed_y_check.setChecked(False)
        self.fixed_y_check.setToolTip("Use consistent Y-axis scaling across all plots for comparison")
        time_layout.addRow("Fixed Y-axis Scaling:", self.fixed_y_check)
        
        self.create_axes_check = QCheckBox()
        self.create_axes_check.setChecked(False)
        self.create_axes_check.setToolTip("Creates a separate SVG file with clean scale bars that can be used in graphics applications")
        time_layout.addRow("Create Separate Axes SVG:", self.create_axes_check)
        
        self.plot_axes_on_trace_check = QCheckBox()
        self.plot_axes_on_trace_check.setChecked(True)
        self.plot_axes_on_trace_check.setToolTip("Adds scale bars directly to the trace plot itself (embedded in the main image)")
        time_layout.addRow("Plot Scale Bars on Trace:", self.plot_axes_on_trace_check)
        
        time_tab.setLayout(time_layout)
        tab_widget.addTab(time_tab, "Time/Axes")
        
        layout.addWidget(tab_widget)
        self.setLayout(layout)
        
        # Set initial state
        self.on_overlay_toggled(False)
    
    def pick_color(self):
        """Open color picker dialog"""
        # Get current color
        current_color_text = self.color_edit.text().strip()
        
        # Try to parse current color
        try:
            if current_color_text.startswith('#'):
                current_color = QColor(current_color_text)
            else:
                current_color = QColor(current_color_text)
        except Exception:
            current_color = QColor('#ffd700')  # Default fallback
        
        # Open color picker
        color = QColorDialog.getColor(current_color, self, "Choose Trace Color")
        
        if color.isValid():
            # Update the text field with hex color
            self.color_edit.setText(color.name())
    
    def update_color_swatch(self, color_text=None):
        """Update the color swatch to show the current color"""
        if color_text is None:
            color_text = self.color_edit.text().strip()
        
        # Try to parse the color
        try:
            if color_text.startswith('#'):
                color = QColor(color_text)
            else:
                color = QColor(color_text)
            
            # If color is valid, update swatch
            if color.isValid():
                self.color_swatch.setStyleSheet(f"""
                    QLabel {{ 
                        background-color: {color.name()}; 
                        border: 1px solid gray; 
                    }}
                """)
            else:
                # Invalid color - show a pattern or default
                self.color_swatch.setStyleSheet("""
                    QLabel { 
                        background-color: white; 
                        border: 1px solid red;
                    }
                """)
        except Exception:
            # Fallback for any parsing errors
            self.color_swatch.setStyleSheet("""
                QLabel { 
                    background-color: white; 
                    border: 1px solid red;
                }
            """)
    
    def update_recording_channel_options(self, available_recordings, available_channels):
        """Update recording and channel combo boxes with available options"""
        # Update recording combo box
        self.recording_combo.clear()
        if available_recordings:
            for recording in available_recordings:
                self.recording_combo.addItem(str(recording), recording)
            self.recording_combo.setEnabled(True)
        else:
            self.recording_combo.addItem("No recordings found", 0)
            self.recording_combo.setEnabled(False)
        
        # Update channel combo box
        self.channel_combo.clear()
        if available_channels:
            for channel in available_channels:
                self.channel_combo.addItem(str(channel), channel)
            self.channel_combo.setEnabled(True)
        else:
            self.channel_combo.addItem("No channels found", 0)
            self.channel_combo.setEnabled(False)
    
    def on_overlay_toggled(self, checked):
        """Enable/disable overlay-specific options"""
        # Enable overlay tab when overlay is checked
        tab_widget = self.findChild(QTabWidget)
        if tab_widget:
            tab_widget.setTabEnabled(1, checked)  # Overlay tab
    
    def get_plot_options(self):
        """Get all plot options as a dictionary"""
        # Get values from combo boxes, fallback to 0 if no valid selection
        recording_index = self.recording_combo.currentData() if self.recording_combo.currentData() is not None else 0
        channel_index = self.channel_combo.currentData() if self.channel_combo.currentData() is not None else 0
        
        return {
            'recording_index': recording_index,
            'channel_index': channel_index,
            'overlay': self.overlay_check.isChecked(),
            'stim_col': self.stim_col_edit.text(),
            'cmap_name': self.cmap_combo.currentText(),
            'cmin': None if self.cmin_spin.value() == -999.99 else self.cmin_spin.value(),
            'cmax': None if self.cmax_spin.value() == -999.99 else self.cmax_spin.value(),
            'show_colorbar': self.colorbar_check.isChecked(),
            'color': self.color_edit.text(),
            'linewidth': self.linewidth_spin.value(),
            'figsize': (self.figsize_width.value(), self.figsize_height.value()),
            'dpi': self.dpi_spin.value(),
            'tmin': None if self.tmin_spin.value() == -9999.99 else self.tmin_spin.value(),
            'tmax': None if self.tmax_spin.value() == -9999.99 else self.tmax_spin.value(),
            'hide_axes': self.hide_axes_check.isChecked(),
            'transparent': self.transparent_check.isChecked(),
            'fixed_y': self.fixed_y_check.isChecked(),
            'create_axes': self.create_axes_check.isChecked(),
            'plot_axes_on_trace': self.plot_axes_on_trace_check.isChecked()
        }


class OutputWidget(QGroupBox):
    """Widget for output file selection and options"""
    
    def __init__(self):
        super().__init__("Output Options")
        self.output_file = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Output file selection
        file_row = QHBoxLayout()
        self.output_label = QLabel("No output file selected\n(Preview-only Mode)")
        self.output_label.setStyleSheet("QLabel { color: palette(disabled-text); font-style: italic; }")
        self.browse_output_button = QPushButton("Choose Output File...")
        self.browse_output_button.clicked.connect(self.browse_output_file)
        self.clear_output_button = QPushButton("Clear")
        self.clear_output_button.clicked.connect(self.clear_output_file)
        
        file_row.addWidget(self.output_label, 1)
        file_row.addWidget(self.browse_output_button)
        file_row.addWidget(self.clear_output_button)
        layout.addLayout(file_row)
        
        self.setLayout(layout)
    
    def browse_output_file(self):
        """Open file dialog to select output file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Plot As",
            "",
            "PNG Files (*.png);;SVG Files (*.svg);;PDF Files (*.pdf);;All Files (*)"
        )
        
        if file_path:
            self.output_file = file_path
            filename = os.path.basename(file_path)
            self.output_label.setText(f"Output: {filename}")
            self.output_label.setStyleSheet("QLabel { font-weight: bold; }")
    
    def clear_output_file(self):
        """Clear output file selection to show plot instead"""
        self.output_file = None
        self.output_label.setText("No output file selected\n(Preview-only Mode)")
        self.output_label.setStyleSheet("QLabel { color: palette(disabled-text); font-style: italic; }")


class EMGPlotterMainWindow(QMainWindow):
    """Main window for the EMG Plotter GUI"""
    
    def __init__(self):
        super().__init__()
        self.worker = None
        self.setup_ui()
        self.setup_window()
    
    def setup_window(self):
        """Configure main window properties"""
        self.setWindowTitle("MonStim Plotter v1.0")

        # Get screen geometry for better window sizing
        screen = QApplication.primaryScreen().geometry()
        screen_width = screen.width()
        screen_height = screen.height()
        
        # Set window size to be 80% of screen size, but with reasonable limits
        window_width = min(max(int(screen_width * 0.8), 800), 1400)
        window_height = min(max(int(screen_height * 0.8), 600), 900)
        
        self.setMinimumSize(800, 600)
        self.resize(window_width, window_height)
        
        # Center the window
        self.move((screen_width - window_width) // 2, (screen_height - window_height) // 2)
        
        # Try to set icon if available
        try:
            # Function to get resource path that works for both development and PyInstaller
            def get_resource_path(relative_path):
                """Get absolute path to resource, works for dev and for PyInstaller"""
                try:
                    # PyInstaller creates a temp folder and stores path in _MEIPASS
                    base_path = sys._MEIPASS
                except Exception:
                    base_path = os.path.abspath(".")
                return os.path.join(base_path, relative_path)
            
            # Look for icon in src folder first, then common locations
            icon_paths = [
                get_resource_path(os.path.join('src', 'icon.png')),
                'src/icon.png',
                'icon.png', 
                'icon.ico', 
            ]
            
            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    self.setWindowIcon(QIcon(icon_path))
                    break
        except Exception:
            pass  # No icon available
    
    def setup_ui(self):
        """Set up the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Left panel for controls
        left_panel = QWidget()
        left_panel.setMaximumWidth(400)
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        
        # File selection widget
        self.file_widget = FileSelectionWidget()
        left_layout.addWidget(self.file_widget)
        
        # Plot options widget
        self.options_widget = PlotOptionsWidget()
        left_layout.addWidget(self.options_widget, 1)  # Give it more space
        
        # Connect file selection to plot options
        self.file_widget.set_file_info_callback(self.options_widget.update_recording_channel_options)
        
        # Output widget
        self.output_widget = OutputWidget()
        left_layout.addWidget(self.output_widget)
        
        # Action buttons
        button_frame = QFrame()
        button_layout = QHBoxLayout()
        button_frame.setLayout(button_layout)
        
        self.preview_button = QPushButton("Preview Plot")
        self.preview_button.clicked.connect(self.preview_plot)
        self.plot_button = QPushButton("Generate Plot")
        self.plot_button.clicked.connect(self.generate_plot)
        
        # Style the buttons
        for btn in [self.preview_button, self.plot_button]:
            btn.setMinimumHeight(35)
            btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        self.plot_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        
        button_layout.addWidget(self.preview_button)
        button_layout.addWidget(self.plot_button)
        left_layout.addWidget(button_frame)
        
        # Right panel for status/progress
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        
        # Status display
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout()
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(200)
        self.status_text.setText("Welcome to EMG Plotter!\n\n1. Select a CSV file\n2. Configure plot options\n3. Choose output file (optional)\n4. Generate plot")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        status_layout.addWidget(self.status_text)
        status_layout.addWidget(self.progress_bar)
        status_group.setLayout(status_layout)
        
        right_layout.addWidget(status_group)
        right_layout.addStretch()  # Push status to top
        
        # Add panels to main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, 1)  # Give right panel more space
    
    def log_message(self, message):
        """Add a message to the status log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.append(f"[{timestamp}] {message}")
        # Auto-scroll to bottom
        cursor = self.status_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.status_text.setTextCursor(cursor)
    
    def preview_plot(self):
        """Preview the plot without saving"""
        if not self.validate_inputs():
            return
        
        self.log_message("Generating preview plot...")
        
        # Get options but force output_file to None for preview
        options = self.options_widget.get_plot_options()
        options.update({
            'csv_file': self.file_widget.csv_file,
            'output_file': None  # Force preview mode
        })
        
        # Set matplotlib to interactive mode for display
        import matplotlib.pyplot as plt
        plt.ion()  # Turn on interactive mode
        
        try:
            # Run plot directly on main thread for preview
            plot_emg_trace(**options)
            self.log_message("Preview plot displayed successfully!")
        except Exception as e:
            self.log_message(f"Error generating preview: {str(e)}")
            QMessageBox.critical(self, "Plot Error", f"Error generating preview:\n{str(e)}")
        finally:
            plt.ioff()  # Turn off interactive mode
    
    def generate_plot(self):
        """Generate and save the plot"""
        if not self.validate_inputs():
            return
        
        # Get all options
        options = self.options_widget.get_plot_options()
        options.update({
            'csv_file': self.file_widget.csv_file,
            'output_file': self.output_widget.output_file
        })
        
        self.log_message("Starting plot generation...")
        
        # If we're saving to a file, we can use worker thread
        # If we're showing the plot, we need to use main thread
        if self.output_widget.output_file:
            # Save to file - can use worker thread
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            
            # Disable buttons during processing
            self.preview_button.setEnabled(False)
            self.plot_button.setEnabled(False)
            
            # Create worker thread
            self.worker = PlottingWorker(plot_emg_trace, **options)
            self.worker.finished.connect(self.on_plot_finished)
            self.worker.error.connect(self.on_plot_error)
            self.worker.progress.connect(self.log_message)
            self.worker.start()
        else:
            # Show plot - must use main thread
            # Set matplotlib to interactive mode for display
            import matplotlib.pyplot as plt
            plt.ion()  # Turn on interactive mode
            
            try:
                plot_emg_trace(**options)
                self.log_message("Plot displayed successfully!")
            except Exception as e:
                self.log_message(f"Error generating plot: {str(e)}")
                QMessageBox.critical(self, "Plot Error", f"Error generating plot:\n{str(e)}")
            finally:
                plt.ioff()  # Turn off interactive mode
    
    def on_plot_finished(self):
        """Handle successful plot completion"""
        self.progress_bar.setVisible(False)
        self.preview_button.setEnabled(True)
        self.plot_button.setEnabled(True)
        
        if self.output_widget.output_file:
            self.log_message(f"Plot saved successfully to: {self.output_widget.output_file}")
            QMessageBox.information(self, "Success", f"Plot saved successfully!\n\nOutput: {self.output_widget.output_file}")
        else:
            self.log_message("Plot displayed successfully!")
    
    def on_plot_error(self, error_message):
        """Handle plot generation error"""
        self.progress_bar.setVisible(False)
        self.preview_button.setEnabled(True)
        self.plot_button.setEnabled(True)
        
        self.log_message(f"Error: {error_message}")
        QMessageBox.critical(self, "Error", f"Error generating plot:\n{error_message}")
    
    def validate_inputs(self):
        """Validate user inputs before plotting"""
        if not self.file_widget.csv_file:
            QMessageBox.warning(self, "Input Error", "Please select a CSV file first.")
            return False
        
        if not os.path.exists(self.file_widget.csv_file):
            QMessageBox.warning(self, "File Error", "Selected CSV file does not exist.")
            return False
        
        return True
    
    def closeEvent(self, event):
        """Handle application closing"""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(self, "Close Application", 
                                       "Plot generation is in progress. Close anyway?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
            
            self.worker.terminate()
            self.worker.wait()
        
        event.accept()


def main():
    """Main application entry point"""
    # Enable high DPI scaling for PyQt6
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    # Check if QApplication already exists (e.g., in Jupyter or other GUI environment)
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        should_exec = True
    else:
        should_exec = False
    
    # Set application properties
    app.setOrganizationName("WorthyLab")
    app.setApplicationName("MonStim Plotter v1.0")
    app.setApplicationVersion("1.0")
    
    # Set a more modern style
    try:
        app.setStyle('Fusion')
    except Exception:
        pass  # Use default style if Fusion not available
    
    # Create and show main window
    window = EMGPlotterMainWindow()
    window.show()
    
    # Run the application only if we created it
    if should_exec:
        return app.exec()
    else:
        return 0


if __name__ == '__main__':
    main()
