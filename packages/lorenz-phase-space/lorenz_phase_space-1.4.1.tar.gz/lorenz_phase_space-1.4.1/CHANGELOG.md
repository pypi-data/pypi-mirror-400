# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [1.3.0] - 2025-12-30

### Added
- **Comprehensive Documentation**: Complete API documentation with detailed parameter descriptions, examples, and best practices
- **Docstrings**: Added NumPy-style docstrings to all classes, methods, and functions in `phase_diagrams.py`
- **Example Notebook**: Interactive Jupyter notebook (`docs/example_usage.ipynb`) demonstrating all features
- **Quick Reference Guide**: One-page reference (`docs/QUICK_REFERENCE.md`) for common operations
- **Enhanced Test Suite**: 30+ comprehensive tests covering all functionality, edge cases, and visual output
- **Visual Verification System**: Test outputs saved to `tests/test_outputs/` for manual inspection
- **Test Classes**: 7 test classes (TestHelperFunctions, TestVisualizerInitialization, TestVisualizerMethods, TestDataPlotting, TestEdgeCases, TestVisualOutput, TestRealDataScenarios)

### Changed
- **Documentation Structure**: Reorganized documentation into `docs/` folder for better organization
- **Testing Documentation**: Moved `TESTING.md` to `tests/` folder alongside test files
- **README**: Complete rewrite with improved structure, quick start examples, and better organization
- **Test Suite**: Complete rewrite of `tests/test_lps.py` with comprehensive coverage

### Documentation
- `docs/API_DOCUMENTATION.md`: Complete API reference (~400 lines)
- `docs/QUICK_REFERENCE.md`: Quick reference guide (~200 lines)
- `docs/example_usage.ipynb`: Interactive example notebook
- `tests/TESTING.md`: Comprehensive testing guide (~500 lines)
- Enhanced `README.md` with better examples and structure

### Notes
- No changes to plotting logic - all visual output remains identical
- Backward compatible - all existing code will work without modifications
- Tests verified and passing

## [1.4.0] - 2026-01-02

### Added
- Discrete colormap for `Ge` across all LPS types using 10 distinct colors (implemented with `BoundaryNorm`).
- New user-configurable reference line width parameters: `h_lw`, `v_lw`, and `diagonal_lw`.

### Changed
- Color normalization now always centers on zero by using the largest absolute value from the plotted `Ge` series to set symmetric boundaries.
- The reference region rendering was reverted to use `axhline`/`axvline` (configurable linewidth) instead of filled regions; the `fill_between` implementation is retained in the codebase commented for future reactivation.
- Example notebook (`docs/example_usage.ipynb`) updated to load real sample data and to avoid deprecated `pd.read_csv(parse_dates=...)` usage.
- Tests updated to use real sample data from `samples/` and to validate the discrete colorbar behavior; test suite remains passing (38 tests).

### Fixed
- Resolved `KeyError: 'size_label'` during `Visualizer` initialization.
- Ensured colorbar displays discrete ticks and boundaries consistently and that plots are centered on zero to avoid interpretation distortions.

### Notes
- Version bump to `1.4.0` includes visualization and API improvements; see updated files for details.

## [1.4.1] - 2026-01-05

### Changed
- Adjusted default marker size intervals in `Visualizer.calculate_marker_size` (intervals revised to improve legend readability and marker scaling).

### Fixed
- Updated CI and packaging metadata to reference the new package version `1.4.1`.

### Notes
- Patch release to apply visualization sizing change and prepare package for publishing.

## [1.2.4] - 2024-07-03

### Bug Fixes
- Wrong parenthesis on labels
- Diagonal line on mixed-zoom plot

## [1.2.3] - 2024-07-01

### Changed
- Barotropic LPS changed to "imports", which uses BKe and BAe. 

## [1.2.2] - 2024-06-27

### Changed
- Changed barotropic LPS for using BKe instead of BKz.
- Test cases on main file now include multiple LPS types.

## [1.2.1] - 2024-02-28

### Changed
- Adjusted automatically setting dynamic limits for colorbar whenever zoom flag is True so the values are always centered around zero.

## [1.2.0] - 2024-02-28

### Changed
- Improved naming conventions for the script and class to enhance clarity and usability and updated repository structure.

## [1.1.1] - 2024-02-28

### Fixed
- `___init__.py` file was missing, causing import errors.

## [1.1.0] - 2024-02-23

### Added
- Dynamic zoom functionality in `LorenzPhaseSpace` class, allowing users to dynamically adjust plot limits based on the dataset's range.
- The ability to pass custom limits for x-axis, y-axis, color, and marker size during class initialization and plotting to enable more flexible visualizations.
- Enhanced error handling for colorbar and legend creation to prevent duplication when plotting multiple datasets.

### Changed
- Modified `LorenzPhaseSpace` class initialization to support new parameters for dynamic limits and zoom functionality, offering improved flexibility for users.
- Updated plot_data method to incorporate dynamic zoom and limit adjustments, ensuring that the visualizations accurately reflect the data being plotted.
- Improved test suite to cover new functionalities and ensure the reliability of dynamic limit adjustments and zoom features.

### Fixed
- Issue where multiple colorbars and legends were created when plotting multiple datasets, now ensuring only the latest colorbar and legend are displayed.

### Optimization
- Enhanced the efficiency of plotting large datasets by optimizing colorbar and legend updates to avoid unnecessary recalculations.


## [1.0.1] - 2024-02-22

### Changed
- **Updated DOcumentation**: Updated 'usage' so it incorporates changes done in 1.0.0

## [1.0.0] - 2024-02-22

### Added
- **Dynamic Plotting**: Introduced functionality for dynamic zoom and plotting data with randomized factors to better test the robustness of the plotting functionalities.
- **Flexible Data Handling**: Added capabilities to handle data plotting more flexibly, allowing for plotting multiple datasets on the same plot structure by calling the data plotting method multiple times.
- **Test Suite Enhancements**: Expanded the test suite to cover new functionalities, including zoom effects and data randomization, ensuring the reliability of new features.

### Changed
- **Refactored Plotting Methodology**: Shifted from a single method handling both plot creation and data plotting to a more modular approach with `create_lps_plot` for setting up the plot environment and `plot_data` for adding data to the plot.
- **Enhanced Plot Customization**: Enhanced the plot customization options, including automatic axis limit adjustments based on the data being plotted and customization of plot annotations and labels.
- **Updated Dependencies**: Addressed deprecation warnings by updating the handling of color maps to align with newer versions of dependencies like `matplotlib` and `cmocean`.

### Fixed
- **Axis Limit Calculation**: Fixed issues related to axis limit calculation in zoomed plots to ensure that plots dynamically adjust to the data's range.
- **Highlighting Specific Data Points**: Implemented functionality to highlight specific data points, such as the point with the maximum marker size, improving the visual analysis capabilities of the plots.
- **Modular Test Architecture**: Refined the test architecture to better align with the refactored plotting functionalities, ensuring that each component of the class is reliably tested.


## [0.0.9] - 2024-01-02

### Bug fixes

- Fixed ploting "zoom=True" when maximum values are lower than 0 and minimum values are higher than 0 (set them to 1 and -1, respectively).

## [0.0.8] - 2024-01-02

### Bug fixes

- Standardized input data as pd.Series for avoinding bugs.

## [0.0.7] - 2024-01-02

### Bug fixes

## [0.0.6] - 2024-01-02

### Bug fixes

## [0.0.5] - 2024-01-02

### Updated Documentation

## [0.0.4] - 2024-01-02

### Bug fixes

## [0.0.3] - 2024-01-02

### Modified

- Updated **README.md**

## [0.0.2] - 2024-01-02

### Modified

- **setup.py**: Integrated with README.md
- **gitignore.py**: included figures generated from testing 
- **.cicleci/congif.yml**: included variables for CircleCI authentication

### Added

- **CHANGELOG.md**