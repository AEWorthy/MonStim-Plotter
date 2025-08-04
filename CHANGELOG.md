# Changelog

All notable changes to MonStim Plotter will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-08-04

### Added
- Initial public release of MonStim Plotter toolkit
- PyQt6-based graphical user interface for EMG data visualization
- Command-line interface with comprehensive options
- Support for single trace and overlay plotting modes
- Multiple output formats (PNG, SVG, PDF)
- Customizable colormaps and styling options
- Time windowing and axis configuration
- Automatic SVG axes generation for vector graphics workflows
- Background processing with progress feedback
- Sample EMG data files for testing and demonstrations
- Comprehensive documentation and user guides
- PyInstaller configuration for standalone Windows executable
- Automated build scripts for distribution

### Technical Features
- Integration with MonStim Analysis CSV output format
- Publication-quality figure generation
- Transparent background support for presentations
- High-DPI output for print publications
- Batch processing capabilities via command line
- Python module for programmatic access
- Error handling and user feedback systems

### Documentation
- Complete README with installation and usage instructions
- Separate GUI user guide with step-by-step tutorials
- Build instructions for creating standalone executables
- Code examples and programming tutorials
- Troubleshooting guides for common issues

### Dependencies
- PyQt6 >= 6.4.0 for GUI framework
- pandas >= 1.3.0 for data handling
- matplotlib >= 3.5.0 for plotting
- numpy >= 1.20.0 for numerical computations
- Pillow >= 8.0.0 for image processing
- PyInstaller >= 5.0.0 for executable building
