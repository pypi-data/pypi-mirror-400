"""
Tests for Oxford theme presets
"""

import pytest
import matplotlib.pyplot as plt
from oxford_matplotlib_theme.presets import (
    PRESETS,
    apply_preset,
    list_presets,
    get_preset_config,
)
from oxford_matplotlib_theme.styles import reset_theme
from oxford_matplotlib_theme.colors import OXFORD_COLORS


class TestPresetDefinitions:
    """Test the PRESETS dictionary."""

    def test_presets_exist(self):
        """Test that PRESETS dictionary exists and has content."""
        assert PRESETS is not None
        assert len(PRESETS) > 0

    def test_minimum_preset_count(self):
        """Test that at least 5 presets are defined."""
        assert len(PRESETS) >= 5

    def test_expected_presets_exist(self):
        """Test that all expected presets exist."""
        expected = ['default', 'presentation', 'print', 'colorblind', 'minimal', 'notebook', 'poster']
        for preset_name in expected:
            assert preset_name in PRESETS, f"Preset '{preset_name}' should exist"

    def test_all_presets_have_required_keys(self):
        """Test that all presets have required configuration keys."""
        required_keys = ['description', 'style_base', 'color_cycle', 'font_scale']
        for preset_name, config in PRESETS.items():
            for key in required_keys:
                assert key in config, f"Preset '{preset_name}' missing key '{key}'"

    def test_all_presets_have_descriptions(self):
        """Test that all presets have non-empty descriptions."""
        for preset_name, config in PRESETS.items():
            assert config['description'], f"Preset '{preset_name}' has empty description"
            assert len(config['description']) > 10, f"Preset '{preset_name}' description too short"

    def test_font_scales_are_positive(self):
        """Test that all font_scale values are positive numbers."""
        for preset_name, config in PRESETS.items():
            font_scale = config['font_scale']
            assert isinstance(font_scale, (int, float)), f"{preset_name} font_scale not numeric"
            assert font_scale > 0, f"{preset_name} font_scale must be positive"

    def test_presentation_has_larger_font_scale(self):
        """Test that presentation preset has font_scale > 1.0."""
        assert PRESETS['presentation']['font_scale'] > 1.0

    def test_poster_has_largest_font_scale(self):
        """Test that poster preset has very large font_scale."""
        assert PRESETS['poster']['font_scale'] >= 1.5


class TestApplyPreset:
    """Test the apply_preset function."""

    def setup_method(self):
        """Reset theme before each test."""
        reset_theme()

    def teardown_method(self):
        """Reset theme after each test."""
        reset_theme()

    def test_apply_default_preset(self):
        """Test applying default preset."""
        apply_preset('default')
        assert plt.rcParams['axes.labelcolor'] == OXFORD_COLORS['oxford_blue']

    def test_apply_presentation_preset(self):
        """Test applying presentation preset."""
        apply_preset('presentation')
        assert plt.rcParams['axes.labelcolor'] == OXFORD_COLORS['oxford_blue']

    def test_apply_all_presets(self):
        """Test that all presets can be applied without error."""
        for preset_name in PRESETS.keys():
            reset_theme()
            apply_preset(preset_name)
            # Should have Oxford Blue in axes
            assert plt.rcParams['axes.labelcolor'] == OXFORD_COLORS['oxford_blue']

    def test_presentation_increases_font_size(self):
        """Test that presentation preset increases font size."""
        # Apply default
        apply_preset('default')
        default_font_size = plt.rcParams['font.size']

        # Apply presentation
        reset_theme()
        apply_preset('presentation')
        presentation_font_size = plt.rcParams['font.size']

        # Presentation should have larger fonts
        assert presentation_font_size > default_font_size

    def test_poster_has_very_large_fonts(self):
        """Test that poster preset has very large fonts."""
        apply_preset('default')
        default_font_size = plt.rcParams['font.size']

        reset_theme()
        apply_preset('poster')
        poster_font_size = plt.rcParams['font.size']

        # Poster should have much larger fonts
        assert poster_font_size > default_font_size * 1.5

    def test_case_insensitive_preset_names(self):
        """Test that preset names are case-insensitive."""
        # These should all work
        reset_theme()
        apply_preset('DEFAULT')

        reset_theme()
        apply_preset('default')

        reset_theme()
        apply_preset('Default')

        # All should apply successfully without error

    def test_invalid_preset_raises_error(self):
        """Test that invalid preset name raises ValueError."""
        with pytest.raises(ValueError):
            apply_preset('nonexistent_preset')

    def test_error_message_lists_available_presets(self):
        """Test that error message lists available presets."""
        try:
            apply_preset('invalid')
        except ValueError as e:
            error_msg = str(e).lower()
            assert 'available' in error_msg or 'preset' in error_msg
            assert 'default' in error_msg

    def test_colorblind_preset_applies(self):
        """Test that colorblind preset applies successfully."""
        apply_preset('colorblind')
        # Should have different color cycle than default
        assert plt.rcParams['axes.labelcolor'] == OXFORD_COLORS['oxford_blue']

    def test_minimal_preset_applies(self):
        """Test that minimal preset applies successfully."""
        apply_preset('minimal')
        assert plt.rcParams['axes.labelcolor'] == OXFORD_COLORS['oxford_blue']


class TestListPresets:
    """Test the list_presets function."""

    def test_list_presets_runs_without_error(self, capsys):
        """Test that list_presets runs without error."""
        list_presets()
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_list_presets_shows_preset_names(self, capsys):
        """Test that list_presets displays preset names."""
        list_presets()
        captured = capsys.readouterr()
        output = captured.out.lower()

        # Should show some preset names
        assert 'default' in output
        assert 'presentation' in output

    def test_list_presets_shows_descriptions(self, capsys):
        """Test that list_presets displays descriptions."""
        list_presets()
        captured = capsys.readouterr()
        output = captured.out

        # Should show description content
        assert 'academic' in output.lower() or 'paper' in output.lower()
        assert 'presentation' in output.lower() or 'slide' in output.lower()

    def test_list_presets_formatted_nicely(self, capsys):
        """Test that output is formatted with separators."""
        list_presets()
        captured = capsys.readouterr()
        output = captured.out

        # Should have some formatting (lines, equals signs, etc.)
        assert '=' in output or '-' in output


class TestGetPresetConfig:
    """Test the get_preset_config function."""

    def test_returns_dict(self):
        """Test that function returns a dictionary."""
        config = get_preset_config('default')
        assert isinstance(config, dict)

    def test_config_has_required_keys(self):
        """Test that returned config has all required keys."""
        config = get_preset_config('default')
        required_keys = ['description', 'style_base', 'color_cycle', 'font_scale']
        for key in required_keys:
            assert key in config

    def test_get_all_preset_configs(self):
        """Test getting config for all presets."""
        for preset_name in PRESETS.keys():
            config = get_preset_config(preset_name)
            assert isinstance(config, dict)
            assert 'description' in config

    def test_case_insensitive(self):
        """Test that preset name is case-insensitive."""
        config1 = get_preset_config('default')
        config2 = get_preset_config('DEFAULT')
        config3 = get_preset_config('Default')

        assert config1 == config2 == config3

    def test_invalid_preset_raises_error(self):
        """Test that invalid preset raises ValueError."""
        with pytest.raises(ValueError):
            get_preset_config('nonexistent')

    def test_returns_copy_not_original(self):
        """Test that function returns a copy, not the original."""
        config = get_preset_config('default')

        # Modify the returned config
        config['font_scale'] = 999.0

        # Original should be unchanged
        assert PRESETS['default']['font_scale'] != 999.0

    def test_presentation_config_values(self):
        """Test that presentation config has expected values."""
        config = get_preset_config('presentation')
        assert config['font_scale'] == 1.4
        assert config['style_base'] == 'seaborn-v0_8-paper'

    def test_poster_config_values(self):
        """Test that poster config has expected values."""
        config = get_preset_config('poster')
        assert config['font_scale'] == 1.8

    def test_colorblind_has_custom_palette(self):
        """Test that colorblind preset has a custom color cycle."""
        config = get_preset_config('colorblind')
        assert config['color_cycle'] is not None
        assert isinstance(config['color_cycle'], list)
        assert len(config['color_cycle']) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
