# Contributing to MonStim Plotter

Thank you for your interest in contributing to MonStim Plotter! This project aims to provide researchers with an intuitive tool for creating publication-quality EMG visualizations.

## Getting Started

### Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/your-username/MonStim-Plotter.git
   cd MonStim-Plotter
   ```

2. **Set up your development environment:**
   ```bash
   pip install -r requirements_gui.txt
   pip install -r requirements_build.txt  # For building executables
   ```

3. **Test your setup:**
   ```bash
   python emg_plotter_gui.py
   python plot_emg.py --help
   ```

## How to Contribute

### Reporting Issues

Before creating an issue, please:
- Check existing issues to avoid duplicates
- Test with the latest version
- Include sample data files when reporting bugs (if possible)

When reporting bugs, please include:
- Operating system and Python version
- Full error messages and stack traces
- Steps to reproduce the issue
- Sample CSV file (if the issue is data-related)

### Suggesting Features

Feature requests are welcome! Please:
- Explain the use case and expected behavior
- Consider how it fits with the project's goal of simplicity
- Provide mockups or examples if applicable

### Code Contributions

1. **Choose an issue or feature**
   - Look for issues labeled "good first issue" for beginners
   - Comment on the issue to let others know you're working on it

2. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes:**
   - Follow the existing code style
   - Add docstrings to new functions
   - Update documentation if needed

4. **Test your changes:**
   - Run the GUI: `python emg_plotter_gui.py`
   - Test CLI functionality: `python plot_emg.py Example\ Data\ 1.csv --overlay`
   - Try building executable: `.\build_exe.ps1` (Windows)

5. **Submit a pull request:**
   - Write a clear description of your changes
   - Reference any related issues
   - Include screenshots for GUI changes

## Code Style Guidelines

### Python Code
- Follow PEP 8 style guidelines
- Use descriptive variable names
- Add docstrings to functions and classes
- Keep functions focused and small when possible

### Documentation
- Update README files when adding features
- Use clear, non-technical language for user-facing documentation
- Include code examples for new functionality

### GUI Development
- Test on different screen sizes/DPI settings
- Ensure accessibility (reasonable font sizes, color contrast)
- Provide helpful error messages and user feedback

## Project Structure

```
MonStim-Plotter/
├── plot_emg.py              # Core plotting functions and CLI
├── emg_plotter_gui.py       # PyQt6 GUI application
├── launcher.py              # Entry point for executable
├── example_usage.py         # Code examples
├── requirements_*.txt       # Dependencies
├── build_exe.ps1           # Build script
├── src/                    # Assets and resources
├── tests/                  # Test files
└── docs/                   # Documentation
```

## Testing

### Manual Testing
- Test with provided sample data files
- Try different parameter combinations
- Test error handling with invalid inputs

### Automated Testing
We welcome contributions to expand test coverage:
- Unit tests for core plotting functions
- GUI integration tests
- Build process validation

## Areas for Contribution

### High Priority
- Cross-platform compatibility improvements
- Performance optimization for large datasets
- Additional export formats
- Improved error handling and user feedback

### Nice to Have
- Additional colormap options
- Batch processing GUI
- Plugin system for custom analyses
- Multi-language support

## Getting Help

- Check existing documentation first
- Ask questions in GitHub Discussions
- Reference related issues when asking for help
- Be patient - this is maintained by researchers in their spare time

## Recognition

All contributors will be recognized in:
- CHANGELOG.md for each release
- GitHub contributors page
- Special thanks in documentation for major contributions

## License

By contributing, you agree that your contributions will be licensed under the same BSD 2-Clause License that covers the project.

Thank you for helping make EMG data visualization more accessible to researchers worldwide!
