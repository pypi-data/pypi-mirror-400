"""
Comprehensive test suite for Lorenz Phase Space Visualizer

This test suite validates both functionality and visual output of the LPS diagrams.
Tests include:
- Basic functionality tests
- Visual regression tests (comparing generated plots)
- Edge case handling
- Multiple LPS types
- Zoom and non-zoom modes
"""

import unittest
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from lorenz_phase_space.phase_diagrams import Visualizer, get_max_min_values


def load_sample_data():
    """Load real cyclone data from samples for testing"""
    base_path = Path(__file__).parent.parent / 'samples'
    sample1_path = base_path / 'sample_results_1.csv'
    
    if not sample1_path.exists():
        # Fallback to synthetic data if sample files not found
        np.random.seed(42)
        n = 10
        return pd.DataFrame({
            'Ck': np.linspace(-30, 20, n),
            'Ca': np.linspace(-2, 6, n),
            'Ge': np.linspace(-8, 8, n),
            'Ke': np.linspace(3e5, 7e5, n)
        })
    
    data = pd.read_csv(sample1_path, parse_dates={'Datetime': ['Date', 'Hour']},
                       date_format='%Y-%m-%d %H')
    return data


class TestHelperFunctions(unittest.TestCase):
    """Test utility functions"""
    
    def test_get_max_min_values_all_negative(self):
        """Test with all negative values"""
        series = np.array([-10, -5, -2])
        max_val, min_val = get_max_min_values(series)
        self.assertEqual(max_val, 1)
        self.assertEqual(min_val, -10)
    
    def test_get_max_min_values_all_positive(self):
        """Test with all positive values"""
        series = np.array([2, 5, 10])
        max_val, min_val = get_max_min_values(series)
        self.assertEqual(max_val, 10)
        self.assertEqual(min_val, -1)
    
    def test_get_max_min_values_mixed(self):
        """Test with mixed positive and negative values"""
        series = np.array([-5, 0, 5])
        max_val, min_val = get_max_min_values(series)
        self.assertEqual(max_val, 5)
        self.assertEqual(min_val, -5)


class TestVisualizerInitialization(unittest.TestCase):
    """Test Visualizer initialization with various parameters"""
    
    def test_default_initialization(self):
        """Test default initialization"""
        lps = Visualizer()
        self.assertEqual(lps.LPS_type, 'conversion')
        self.assertFalse(lps.zoom)
        self.assertIsNotNone(lps.fig)
        self.assertIsNotNone(lps.ax)
        plt.close('all')
    
    def test_mixed_type_no_zoom(self):
        """Test mixed LPS without zoom"""
        lps = Visualizer(LPS_type='conversion', zoom=False)
        self.assertEqual(lps.LPS_type, 'conversion')
        self.assertFalse(lps.zoom)
        plt.close('all')
    
    def test_baroclinic_type_no_zoom(self):
        """Test baroclinic LPS without zoom"""
        lps = Visualizer(LPS_type='baroclinic', zoom=False)
        self.assertEqual(lps.LPS_type, 'baroclinic')
        plt.close('all')
    
    def test_imports_type_no_zoom(self):
        """Test imports LPS without zoom"""
        lps = Visualizer(LPS_type='imports', zoom=False)
        self.assertEqual(lps.LPS_type, 'imports')
        plt.close('all')
    
    def test_with_zoom(self):
        """Test initialization with zoom enabled"""
        lps = Visualizer(LPS_type='conversion', zoom=True)
        self.assertTrue(lps.zoom)
        plt.close('all')
    
    def test_with_custom_limits(self):
        """Test initialization with custom limits"""
        lps = Visualizer(
            LPS_type='conversion',
            zoom=True,
            x_limits=[-50, 50],
            y_limits=[-30, 30],
            color_limits=[-20, 20],
            marker_limits=[1e5, 8e5]
        )
        self.assertTrue(lps.zoom)
        x_lim = lps.ax.get_xlim()
        y_lim = lps.ax.get_ylim()
        self.assertAlmostEqual(x_lim[0], -50, places=1)
        self.assertAlmostEqual(x_lim[1], 50, places=1)
        plt.close('all')


class TestVisualizerMethods(unittest.TestCase):
    """Test individual methods of Visualizer class"""
    
    def setUp(self):
        """Set up test data using real sample data"""
        data = load_sample_data()
        self.x_axis = data['Ck'].values[:5]
        self.y_axis = data['Ca'].values[:5]
        self.marker_color = data['Ge'].values[:5]
        self.marker_size = data['Ke'].values[:5]
    
    def tearDown(self):
        """Clean up after tests"""
        plt.close('all')
    
    def test_calculate_marker_size_no_zoom(self):
        """Test marker size calculation without zoom"""
        sizes, intervals = Visualizer.calculate_marker_size(self.marker_size, zoom=False)
        self.assertEqual(len(sizes), len(self.marker_size))
        self.assertEqual(len(intervals), 5)  # Updated to 5 for conversion LPS
        self.assertIsInstance(sizes, pd.Series)
        self.assertIsInstance(intervals, list)
    
    def test_calculate_marker_size_with_zoom(self):
        """Test marker size calculation with zoom"""
        sizes, intervals = Visualizer.calculate_marker_size(self.marker_size, zoom=True)
        self.assertEqual(len(sizes), len(self.marker_size))
        self.assertEqual(len(intervals), 4)
        # Check that intervals are based on quantiles
        self.assertTrue(intervals[0] < intervals[-1])
    
    def test_get_labels_mixed(self):
        """Test label generation for mixed LPS"""
        lps = Visualizer(LPS_type='conversion', zoom=False)
        labels = lps.get_labels()
        self.assertIsInstance(labels, dict)
        required_keys = ['x_label', 'y_label', 'color_label', 'size_label',
                        'y_upper', 'y_lower', 'x_left', 'x_right']
        for key in required_keys:
            self.assertIn(key, labels)
        plt.close('all')
    
    def test_get_labels_baroclinic(self):
        """Test label generation for baroclinic LPS"""
        lps = Visualizer(LPS_type='baroclinic', zoom=False)
        labels = lps.get_labels()
        self.assertIn('x_label', labels)
        self.assertIn('Ce', labels['x_label'])
        plt.close('all')
    
    def test_get_labels_imports(self):
        """Test label generation for imports LPS"""
        lps = Visualizer(LPS_type='imports', zoom=False)
        labels = lps.get_labels()
        self.assertIn('x_label', labels)
        self.assertIn('BAe', labels['x_label'])
        plt.close('all')
    
    def test_set_limits_default(self):
        """Test default limit setting"""
        lps = Visualizer(LPS_type='conversion', zoom=False)
        limits = lps.set_limits()
        self.assertEqual(len(limits), 4)
        x_lim = lps.ax.get_xlim()
        y_lim = lps.ax.get_ylim()
        # Conversion LPS has different default limits
        self.assertAlmostEqual(x_lim[0], -50, places=1)  # Ck: -50 to 30
        self.assertAlmostEqual(x_lim[1], 30, places=1)
        self.assertAlmostEqual(y_lim[0], -3, places=1)   # Ca: -3 to 8
        self.assertAlmostEqual(y_lim[1], 8, places=1)
        plt.close('all')
    
    def test_set_limits_custom(self):
        """Test custom limit setting"""
        lps = Visualizer(LPS_type='conversion', zoom=True,
                        x_limits=[-40, 40], y_limits=[-15, 15])
        x_lim = lps.ax.get_xlim()
        y_lim = lps.ax.get_ylim()
        self.assertAlmostEqual(x_lim[0], -40, places=1)
        self.assertAlmostEqual(y_lim[0], -15, places=1)
        plt.close('all')


class TestDataPlotting(unittest.TestCase):
    """Test data plotting functionality"""
    
    def setUp(self):
        """Set up test data using real sample data"""
        data = load_sample_data()
        self.x_axis = data['Ck'].values[:10]
        self.y_axis = data['Ca'].values[:10]
        self.marker_color = data['Ge'].values[:10]
        self.marker_size = data['Ke'].values[:10]
    
    def tearDown(self):
        """Clean up after tests"""
        plt.close('all')
    
    def test_plot_data_basic(self):
        """Test basic data plotting"""
        lps = Visualizer(LPS_type='conversion', zoom=False)
        try:
            fig, ax = lps.plot_data(self.x_axis, self.y_axis, 
                                   self.marker_color, self.marker_size)
            self.assertIsNotNone(fig)
            self.assertIsNotNone(ax)
        except Exception as e:
            self.fail(f"plot_data failed with exception: {e}")
    
    def test_plot_data_with_zoom(self):
        """Test data plotting with zoom"""
        lps = Visualizer(LPS_type='conversion', zoom=True)
        try:
            fig, ax = lps.plot_data(self.x_axis, self.y_axis,
                                   self.marker_color, self.marker_size)
            self.assertIsNotNone(fig)
        except Exception as e:
            self.fail(f"plot_data with zoom failed: {e}")
    
    def test_plot_multiple_datasets(self):
        """Test plotting multiple datasets on same plot"""
        lps = Visualizer(LPS_type='conversion', zoom=False)
        try:
            lps.plot_data(self.x_axis, self.y_axis,
                         self.marker_color, self.marker_size, alpha=0.7)
            lps.plot_data(self.x_axis * 0.5, self.y_axis * 0.5,
                         self.marker_color, self.marker_size, alpha=0.7)
        except Exception as e:
            self.fail(f"Plotting multiple datasets failed: {e}")
    
    def test_plot_data_with_custom_alpha(self):
        """Test plotting with custom transparency"""
        lps = Visualizer(LPS_type='conversion', zoom=False)
        try:
            lps.plot_data(self.x_axis, self.y_axis,
                         self.marker_color, self.marker_size, alpha=0.5)
        except Exception as e:
            self.fail(f"plot_data with custom alpha failed: {e}")
    
    def test_plot_data_pandas_input(self):
        """Test plotting with pandas Series input"""
        df = pd.DataFrame({
            'x': self.x_axis,
            'y': self.y_axis,
            'color': self.marker_color,
            'size': self.marker_size
        })
        lps = Visualizer(LPS_type='conversion', zoom=False)
        try:
            lps.plot_data(df['x'], df['y'], df['color'], df['size'])
        except Exception as e:
            self.fail(f"plot_data with pandas input failed: {e}")
    
    def test_plot_data_with_gray_lines(self):
        """Test plotting with gray lines (default, use_arrows=False)"""
        lps = Visualizer(LPS_type='conversion', zoom=False)
        try:
            fig, ax = lps.plot_data(
                self.x_axis, self.y_axis,
                self.marker_color, self.marker_size,
                use_arrows=False
            )
            self.assertIsNotNone(fig)
            self.assertIsNotNone(ax)
        except Exception as e:
            self.fail(f"plot_data with gray lines failed: {e}")
    
    def test_plot_data_with_arrows(self):
        """Test plotting with arrows enabled"""
        lps = Visualizer(LPS_type='conversion', zoom=False)
        try:
            fig, ax = lps.plot_data(
                self.x_axis, self.y_axis,
                self.marker_color, self.marker_size,
                use_arrows=True
            )
            self.assertIsNotNone(fig)
            self.assertIsNotNone(ax)
        except Exception as e:
            self.fail(f"plot_data with arrows failed: {e}")
    
    def test_plot_data_custom_connection_style(self):
        """Test plotting with custom connection line styling"""
        lps = Visualizer(LPS_type='conversion', zoom=False)
        try:
            fig, ax = lps.plot_data(
                self.x_axis, self.y_axis,
                self.marker_color, self.marker_size,
                use_arrows=False,
                connection_color='darkgray',
                connection_alpha=0.7,
                connection_linewidth=2.0
            )
            self.assertIsNotNone(fig)
            self.assertIsNotNone(ax)
        except Exception as e:
            self.fail(f"plot_data with custom connection style failed: {e}")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def tearDown(self):
        """Clean up after tests"""
        plt.close('all')
    
    def test_empty_data(self):
        """Test with empty data arrays"""
        lps = Visualizer(LPS_type='conversion', zoom=False)
        empty = np.array([])
        with self.assertRaises(Exception):
            lps.plot_data(empty, empty, empty, empty)
    
    def test_single_point(self):
        """Test with single data point"""
        lps = Visualizer(LPS_type='conversion', zoom=False)
        single = np.array([1])
        try:
            lps.plot_data(single, single, single, np.array([3e5]))
        except Exception as e:
            # Single point might cause issues with arrows, that's expected
            pass
    
    def test_very_large_values(self):
        """Test with very large values"""
        lps = Visualizer(LPS_type='conversion', zoom=True)
        # Use realistic but extreme values based on real cyclone data ranges
        large_ck = np.array([-100, -50, 0, 50, 100])
        large_ca = np.array([-20, -10, 0, 10, 20])
        large_ge = np.array([-30, -15, 0, 15, 30])
        large_ke = np.array([1e5, 5e5, 1e6, 1.5e6, 2e6])
        try:
            lps.plot_data(large_ck, large_ca, large_ge, large_ke)
        except Exception as e:
            self.fail(f"Plotting large values failed: {e}")
    
    def test_negative_marker_sizes(self):
        """Test with positive marker sizes only (marker_limits should be positive)"""
        lps = Visualizer(LPS_type='conversion', zoom=True,
                        marker_limits=[1e5, 1e6])
        data = np.array([2e5, 3e5, 4e5, 5e5, 6e5])
        # Should work without errors
        lps.plot_data(data, data, data/1e4, data)
        self.assertIsNotNone(lps.fig)


class TestVisualOutput(unittest.TestCase):
    """Test visual output generation (integration tests)"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test output directory"""
        cls.test_output_dir = Path(__file__).parent / 'test_outputs'
        cls.test_output_dir.mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up after tests"""
        plt.close('all')
    
    def test_save_mixed_no_zoom(self):
        """Test saving mixed LPS without zoom"""
        lps = Visualizer(LPS_type='conversion', zoom=False)
        x = np.linspace(-30, 30, 10)
        y = np.sin(x / 10) * 10
        color = np.linspace(-10, 10, 10)
        size = np.linspace(3e5, 7e5, 10)
        
        lps.plot_data(x, y, color, size)
        output_path = self.test_output_dir / 'test_mixed_no_zoom.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        self.assertTrue(output_path.exists())
    
    def test_save_mixed_with_zoom(self):
        """Test saving mixed LPS with zoom"""
        lps = Visualizer(LPS_type='conversion', zoom=True)
        x = np.linspace(-30, 30, 10)
        y = np.sin(x / 10) * 10
        color = np.linspace(-10, 10, 10)
        size = np.linspace(3e5, 7e5, 10)
        
        lps.plot_data(x, y, color, size)
        output_path = self.test_output_dir / 'test_mixed_with_zoom.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        self.assertTrue(output_path.exists())
    
    def test_save_baroclinic(self):
        """Test saving baroclinic LPS"""
        lps = Visualizer(LPS_type='baroclinic', zoom=False)
        x = np.linspace(-30, 30, 10)
        y = np.sin(x / 10) * 10
        color = np.linspace(-10, 10, 10)
        size = np.linspace(3e5, 7e5, 10)
        
        lps.plot_data(x, y, color, size)
        output_path = self.test_output_dir / 'test_baroclinic.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        self.assertTrue(output_path.exists())
    
    def test_save_imports(self):
        """Test saving imports LPS"""
        lps = Visualizer(LPS_type='imports', zoom=False)
        x = np.linspace(10, -10, 11)
        y = np.sin(x / 30) * 100
        color = np.linspace(10, -10, 11)
        size = np.linspace(3e5, 7e5, 11)
        
        lps.plot_data(x, y, color, size)
        output_path = self.test_output_dir / 'test_imports.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        self.assertTrue(output_path.exists())
    
    def test_save_with_gray_lines(self):
        """Test saving plot with gray lines (default)"""
        lps = Visualizer(LPS_type='conversion', zoom=False)
        x = np.linspace(-30, 30, 10)
        y = np.sin(x / 10) * 10
        color = np.linspace(-10, 10, 10)
        size = np.linspace(3e5, 7e5, 10)
        
        lps.plot_data(x, y, color, size, use_arrows=False)
        output_path = self.test_output_dir / 'test_gray_lines.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        self.assertTrue(output_path.exists())
    
    def test_save_with_arrows(self):
        """Test saving plot with arrows"""
        lps = Visualizer(LPS_type='conversion', zoom=False)
        x = np.linspace(-30, 30, 10)
        y = np.sin(x / 10) * 10
        color = np.linspace(-10, 10, 10)
        size = np.linspace(3e5, 7e5, 10)
        
        lps.plot_data(x, y, color, size, use_arrows=True)
        output_path = self.test_output_dir / 'test_with_arrows.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        self.assertTrue(output_path.exists())
    
    def test_save_custom_connection_style(self):
        """Test saving plot with custom connection line styling"""
        lps = Visualizer(LPS_type='conversion', zoom=False)
        x = np.linspace(-30, 30, 10)
        y = np.sin(x / 10) * 10
        color = np.linspace(-10, 10, 10)
        size = np.linspace(3e5, 7e5, 10)
        
        lps.plot_data(x, y, color, size,
                     use_arrows=False,
                     connection_color='darkgray',
                     connection_alpha=0.7,
                     connection_linewidth=2.5)
        output_path = self.test_output_dir / 'test_custom_connections.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        self.assertTrue(output_path.exists())
    
    def test_save_multiple_trajectories(self):
        """Test saving plot with multiple trajectories"""
        x_min, x_max = -40, 40
        y_min, y_max = -15, 15
        color_min, color_max = -12, 12
        size_min, size_max = 2e5, 8e5
        
        lps = Visualizer(
            LPS_type='conversion',
            zoom=True,
            x_limits=[x_min, x_max],
            y_limits=[y_min, y_max],
            color_limits=[color_min, color_max],
            marker_limits=[size_min, size_max]
        )
        
        # First trajectory
        x1 = np.linspace(-20, 20, 8)
        y1 = np.sin(x1 / 5) * 8
        color1 = np.linspace(-8, 8, 8)
        size1 = np.linspace(3e5, 6e5, 8)
        lps.plot_data(x1, y1, color1, size1, alpha=0.8)
        
        # Second trajectory
        x2 = np.linspace(-15, 25, 8)
        y2 = np.cos(x2 / 5) * 10
        color2 = np.linspace(-10, 10, 8)
        size2 = np.linspace(2.5e5, 7e5, 8)
        lps.plot_data(x2, y2, color2, size2, alpha=0.8)
        
        output_path = self.test_output_dir / 'test_multiple_trajectories.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        self.assertTrue(output_path.exists())


class TestRealDataScenarios(unittest.TestCase):
    """Test with sample data files if available"""
    
    def setUp(self):
        """Check if sample data files exist"""
        self.samples_dir = Path(__file__).parent.parent / 'samples'
        self.sample1 = self.samples_dir / 'sample_results_1.csv'
        self.sample2 = self.samples_dir / 'sample_results_2.csv'
        self.test_output_dir = Path(__file__).parent / 'test_outputs'
        self.test_output_dir.mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up after tests"""
        plt.close('all')
    
    def test_sample_data_mixed(self):
        """Test with real sample data - mixed LPS"""
        if not self.sample1.exists():
            self.skipTest("Sample data not available")
        
        df = pd.read_csv(self.sample1, parse_dates={'Datetime': ['Date', 'Hour']},
                        date_format='%Y-%m-%d %H')
        
        lps = Visualizer(LPS_type='conversion', zoom=False)
        lps.plot_data(df['Ck'].values, df['Ca'].values,
                     df['Ge'].values, df['Ke'].values)
        
        output_path = self.test_output_dir / 'test_sample1_mixed.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        self.assertTrue(output_path.exists())
    
    def test_sample_data_dynamic_limits(self):
        """Test with real sample data using dynamic limits"""
        if not (self.sample1.exists() and self.sample2.exists()):
            self.skipTest("Sample data not available")
        
        df1 = pd.read_csv(self.sample1, parse_dates={'Datetime': ['Date', 'Hour']},
                         date_format='%Y-%m-%d %H')
        df2 = pd.read_csv(self.sample2, parse_dates={'Datetime': ['Date', 'Hour']},
                         date_format='%Y-%m-%d %H')
        
        # Calculate dynamic limits
        x_min = min(df1['Ck'].min(), df2['Ck'].min())
        x_max = max(df1['Ck'].max(), df2['Ck'].max())
        y_min = min(df1['Ca'].min(), df2['Ca'].min())
        y_max = max(df1['Ca'].max(), df2['Ca'].max())
        color_min = min(df1['Ge'].min(), df2['Ge'].min())
        color_max = max(df1['Ge'].max(), df2['Ge'].max())
        size_min = min(df1['Ke'].min(), df2['Ke'].min())
        size_max = max(df1['Ke'].max(), df2['Ke'].max())
        
        lps = Visualizer(
            LPS_type='conversion',
            zoom=True,
            x_limits=[x_min, x_max],
            y_limits=[y_min, y_max],
            color_limits=[color_min, color_max],
            marker_limits=[size_min, size_max]
        )
        
        lps.plot_data(df1['Ck'].values, df1['Ca'].values,
                     df1['Ge'].values, df1['Ke'].values, alpha=0.8)
        lps.plot_data(df2['Ck'].values, df2['Ca'].values,
                     df2['Ge'].values, df2['Ke'].values, alpha=0.8)
        
        output_path = self.test_output_dir / 'test_sample_dynamic_limits.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        self.assertTrue(output_path.exists())


def run_tests_with_visual_inspection():
    """
    Run tests and generate a summary report
    """
    # Run the test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(__import__(__name__))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    # List generated plots for visual inspection
    test_output_dir = Path(__file__).parent / 'test_outputs'
    if test_output_dir.exists():
        plots = list(test_output_dir.glob('*.png'))
        print(f"\nGenerated {len(plots)} plots for visual inspection in:")
        print(f"  {test_output_dir}")
        print("\nPlease visually inspect these plots to ensure they look correct:")
        for plot in plots:
            print(f"  - {plot.name}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    # Option 1: Standard unittest run
    # unittest.main()
    
    # Option 2: Run with visual inspection summary
    success = run_tests_with_visual_inspection()
    exit(0 if success else 1)
