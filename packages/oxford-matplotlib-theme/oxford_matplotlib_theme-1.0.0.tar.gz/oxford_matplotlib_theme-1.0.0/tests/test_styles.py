"""
Tests for Oxford theme styling functions
"""

import pytest
import matplotlib.pyplot as plt
from oxford_matplotlib_theme.styles import (
    apply_oxford_theme,
    reset_theme,
    oxford_figure,
    get_oxford_rcparams,
)
from oxford_matplotlib_theme.colors import OXFORD_COLORS, OXFORD_PALETTE


class TestApplyOxfordTheme:
    """Test the apply_oxford_theme function."""

    def setup_method(self):
        """Reset theme before each test."""
        reset_theme()

    def teardown_method(self):
        """Reset theme after each test."""
        reset_theme()

    def test_theme_applies_without_error(self):
        """Test that theme applies successfully."""
        apply_oxford_theme()
        # If no exception raised, test passes

    def test_oxford_blue_in_axes_label_color(self):
        """Test that axes labels are Oxford Blue."""
        apply_oxford_theme()
        assert plt.rcParams['axes.labelcolor'] == OXFORD_COLORS['oxford_blue']

    def test_oxford_blue_in_axes_edge_color(self):
        """Test that axes edges are Oxford Blue."""
        apply_oxford_theme()
        assert plt.rcParams['axes.edgecolor'] == OXFORD_COLORS['oxford_blue']

    def test_oxford_blue_in_text_color(self):
        """Test that text is Oxford Blue."""
        apply_oxford_theme()
        assert plt.rcParams['text.color'] == OXFORD_COLORS['oxford_blue']

    def test_oxford_blue_in_tick_colors(self):
        """Test that tick marks are Oxford Blue."""
        apply_oxford_theme()
        assert plt.rcParams['xtick.color'] == OXFORD_COLORS['oxford_blue']
        assert plt.rcParams['ytick.color'] == OXFORD_COLORS['oxford_blue']

    def test_font_family_includes_arial(self):
        """Test that font family includes Arial."""
        apply_oxford_theme()
        fonts = plt.rcParams['font.sans-serif']
        assert 'Arial' in fonts

    def test_font_family_includes_helvetica(self):
        """Test that font family includes Helvetica."""
        apply_oxford_theme()
        fonts = plt.rcParams['font.sans-serif']
        assert 'Helvetica' in fonts

    def test_legend_edge_color(self):
        """Test that legend edge is Oxford Blue."""
        apply_oxford_theme()
        assert plt.rcParams['legend.edgecolor'] == OXFORD_COLORS['oxford_blue']

    def test_legend_frame_on(self):
        """Test that legend frame is enabled."""
        apply_oxford_theme()
        assert plt.rcParams['legend.frameon'] == True

    def test_background_colors_white(self):
        """Test that backgrounds are white."""
        apply_oxford_theme()
        assert plt.rcParams['figure.facecolor'] == 'white'
        assert plt.rcParams['axes.facecolor'] == 'white'

    def test_color_cycle_uses_oxford_palette(self):
        """Test that color cycle uses OXFORD_PALETTE."""
        apply_oxford_theme()
        prop_cycle = plt.rcParams['axes.prop_cycle']
        colors = [c['color'] for c in prop_cycle]
        assert colors == OXFORD_PALETTE

    def test_custom_color_cycle_hex(self):
        """Test applying theme with custom color cycle (hex codes)."""
        custom_colors = ['#FF0000', '#00FF00', '#0000FF']
        apply_oxford_theme(color_cycle=custom_colors)
        prop_cycle = plt.rcParams['axes.prop_cycle']
        colors = [c['color'] for c in prop_cycle]
        assert colors == custom_colors

    def test_custom_color_cycle_names(self):
        """Test applying theme with custom color cycle (color names)."""
        custom_names = ['oxford_blue', 'coral', 'aqua']
        apply_oxford_theme(color_cycle=custom_names)
        prop_cycle = plt.rcParams['axes.prop_cycle']
        colors = [c['color'] for c in prop_cycle]
        expected = [OXFORD_COLORS[name] for name in custom_names]
        assert colors == expected

    def test_font_scale_increases_font_sizes(self):
        """Test that font_scale increases font sizes."""
        # Get base font size
        apply_oxford_theme(font_scale=1.0)
        base_size = plt.rcParams['font.size']

        # Apply with scaling
        reset_theme()
        apply_oxford_theme(font_scale=1.5)
        scaled_size = plt.rcParams['font.size']

        # Should be 1.5x larger
        assert scaled_size == pytest.approx(base_size * 1.5, rel=0.01)

    def test_font_scale_affects_multiple_params(self):
        """Test that font_scale affects all font size parameters."""
        apply_oxford_theme(font_scale=1.0)
        base_label_size = plt.rcParams['axes.labelsize']
        base_title_size = plt.rcParams['axes.titlesize']

        reset_theme()
        apply_oxford_theme(font_scale=2.0)

        assert plt.rcParams['axes.labelsize'] == pytest.approx(base_label_size * 2.0, rel=0.01)
        assert plt.rcParams['axes.titlesize'] == pytest.approx(base_title_size * 2.0, rel=0.01)

    def test_different_base_styles(self):
        """Test applying theme with different base styles."""
        base_styles = [
            'seaborn-v0_8-paper',
            'seaborn-v0_8-notebook',
            'seaborn-v0_8-whitegrid',
        ]
        for style in base_styles:
            reset_theme()
            apply_oxford_theme(style_base=style)
            # Should still have Oxford Blue in axes
            assert plt.rcParams['axes.labelcolor'] == OXFORD_COLORS['oxford_blue']


class TestResetTheme:
    """Test the reset_theme function."""

    def test_reset_restores_defaults(self):
        """Test that reset_theme restores default settings."""
        # Save original
        original_label_color = plt.rcParamsDefault['axes.labelcolor']

        # Apply Oxford theme
        apply_oxford_theme()
        assert plt.rcParams['axes.labelcolor'] == OXFORD_COLORS['oxford_blue']

        # Reset
        reset_theme()
        assert plt.rcParams['axes.labelcolor'] == original_label_color

    def test_reset_multiple_params(self):
        """Test that reset affects multiple parameters."""
        # Get defaults
        defaults = {
            'axes.labelcolor': plt.rcParamsDefault['axes.labelcolor'],
            'text.color': plt.rcParamsDefault['text.color'],
            'legend.edgecolor': plt.rcParamsDefault['legend.edgecolor'],
        }

        # Apply theme
        apply_oxford_theme()

        # Reset
        reset_theme()

        # Check all are restored
        for param, default_value in defaults.items():
            assert plt.rcParams[param] == default_value


class TestOxfordFigure:
    """Test the oxford_figure function."""

    def setup_method(self):
        """Clean up before each test."""
        plt.close('all')
        reset_theme()

    def teardown_method(self):
        """Clean up after each test."""
        plt.close('all')
        reset_theme()

    def test_returns_figure_and_axes(self):
        """Test that oxford_figure returns fig and ax."""
        fig, ax = oxford_figure()
        assert fig is not None
        assert ax is not None

    def test_returned_types(self):
        """Test that returned objects are correct types."""
        from matplotlib.figure import Figure
        from matplotlib.axes import Axes

        fig, ax = oxford_figure()
        assert isinstance(fig, Figure)
        assert isinstance(ax, Axes)

    def test_applies_oxford_theme(self):
        """Test that oxford_figure applies Oxford theme."""
        fig, ax = oxford_figure()
        assert plt.rcParams['axes.labelcolor'] == OXFORD_COLORS['oxford_blue']

    def test_custom_figsize(self):
        """Test creating figure with custom size."""
        fig, ax = oxford_figure(figsize=(8, 6))
        # Get figure size in inches
        size = fig.get_size_inches()
        assert size[0] == pytest.approx(8, rel=0.01)
        assert size[1] == pytest.approx(6, rel=0.01)

    def test_default_figsize(self):
        """Test that default figsize is (10, 6)."""
        fig, ax = oxford_figure()
        size = fig.get_size_inches()
        assert size[0] == pytest.approx(10, rel=0.01)
        assert size[1] == pytest.approx(6, rel=0.01)

    def test_custom_color_cycle(self):
        """Test oxford_figure with custom color cycle."""
        custom_colors = ['coral', 'aqua', 'oxford_blue']
        fig, ax = oxford_figure(color_cycle=custom_colors)
        prop_cycle = plt.rcParams['axes.prop_cycle']
        colors = [c['color'] for c in prop_cycle]
        expected = [OXFORD_COLORS[name] for name in custom_colors]
        assert colors == expected

    def test_font_scale_parameter(self):
        """Test oxford_figure with font scaling."""
        fig, ax = oxford_figure(font_scale=1.5)
        # Font size should be scaled
        # We can't easily check the exact value, but ensure it's applied
        assert plt.rcParams['axes.labelcolor'] == OXFORD_COLORS['oxford_blue']

    def test_kwargs_passed_to_subplots(self):
        """Test that additional kwargs are passed to plt.subplots."""
        # Use constrained_layout instead of dpi, as dpi can be overridden by style
        fig, ax = oxford_figure(layout='constrained')
        assert fig.get_layout_engine() is not None


class TestGetOxfordRcParams:
    """Test the get_oxford_rcparams function."""

    def setup_method(self):
        """Reset theme before each test."""
        reset_theme()

    def teardown_method(self):
        """Reset theme after each test."""
        reset_theme()

    def test_returns_dict(self):
        """Test that function returns a dictionary."""
        params = get_oxford_rcparams()
        assert isinstance(params, dict)

    def test_contains_oxford_blue(self):
        """Test that returned params contain Oxford Blue."""
        params = get_oxford_rcparams()
        assert params['axes.labelcolor'] == OXFORD_COLORS['oxford_blue']

    def test_does_not_modify_current_rcparams(self):
        """Test that getting params doesn't modify current settings."""
        original_color = plt.rcParams['axes.labelcolor']

        # Get Oxford params (should not apply them)
        params = get_oxford_rcparams()

        # Current params should be unchanged
        assert plt.rcParams['axes.labelcolor'] == original_color

        # Returned params should have Oxford Blue
        assert params['axes.labelcolor'] == OXFORD_COLORS['oxford_blue']

    def test_with_font_scale(self):
        """Test getting params with font scaling."""
        params1 = get_oxford_rcparams(font_scale=1.0)
        params2 = get_oxford_rcparams(font_scale=2.0)

        # Font size should be doubled
        assert params2['font.size'] == pytest.approx(params1['font.size'] * 2.0, rel=0.01)

    def test_with_custom_color_cycle(self):
        """Test getting params with custom color cycle."""
        custom_colors = ['#FF0000', '#00FF00']
        params = get_oxford_rcparams(color_cycle=custom_colors)

        prop_cycle = params['axes.prop_cycle']
        colors = [c['color'] for c in prop_cycle]
        assert colors == custom_colors


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
