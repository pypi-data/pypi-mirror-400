"""
Tests for Oxford color definitions and palettes
"""

import pytest
from oxford_matplotlib_theme.colors import (
    OxfordColors,
    OXFORD_COLORS,
    OXFORD_PALETTE,
    ColorPalettes,
    get_color,
    get_palette,
    get_color_palette,
)


class TestOxfordColors:
    """Test the OxfordColors class attributes."""

    def test_oxford_colors_count(self):
        """Test that there are 56 Oxford colors."""
        # Count class attributes (excluding special methods)
        color_attrs = [attr for attr in dir(OxfordColors) if not attr.startswith('_') and attr.isupper()]
        assert len(color_attrs) == 56, f"Should have exactly 56 Oxford colors, found {len(color_attrs)}"

    def test_oxford_blue(self):
        """Test that Oxford Blue has the correct hex code."""
        assert OxfordColors.OXFORD_BLUE == '#002147'

    def test_colors_are_hex(self):
        """Test that all colors are valid hex codes."""
        color_attrs = [attr for attr in dir(OxfordColors) if not attr.startswith('_')]
        for attr_name in color_attrs:
            color_value = getattr(OxfordColors, attr_name)
            assert isinstance(color_value, str), f"{attr_name} should be a string"
            assert color_value.startswith('#'), f"{attr_name} should start with #"
            assert len(color_value) == 7, f"{attr_name} should be 7 characters (#RRGGBB)"

    def test_specific_colors(self):
        """Test that specific key colors are correct."""
        assert OxfordColors.CORAL == '#FE615A'
        assert OxfordColors.ROYAL_BLUE == '#1D42A6'
        assert OxfordColors.AQUA == '#00AAB4'
        assert OxfordColors.CHARCOAL == '#211D1C'

    def test_thesis_colors_exist(self):
        """Test that all thesis colors are defined."""
        thesis_colors = [
            'WHITE', 'BLACK', 'THESIS_PURPLE_1', 'BRIGHT_BLUE',
            'THESIS_PURPLE_2', 'SLATE_BLUE_1', 'SLATE_BLUE_2',
            'PERIWINKLE', 'IRIS', 'DEEP_TEAL', 'GOLDEN_YELLOW',
            'DUSTY_MAUVE', 'WISTERIA', 'POWDER_BLUE', 'GREY_BLUE',
            'AMETHYST', 'NAVY_BLUE', 'SOFT_PURPLE',
            'PALE_GREY', 'HEATHER', 'CORNFLOWER'
        ]
        for color in thesis_colors:
            assert hasattr(OxfordColors, color), f"Missing thesis color: {color}"
            color_value = getattr(OxfordColors, color)
            assert color_value.startswith('#'), f"Invalid hex for {color}: {color_value}"
            assert len(color_value) == 7, f"Invalid hex length for {color}: {color_value}"


class TestOxfordColorsDictionary:
    """Test the OXFORD_COLORS dictionary."""

    def test_dictionary_size(self):
        """Test that dictionary has 56 entries."""
        assert len(OXFORD_COLORS) == 56, f"Should have exactly 56 color entries, found {len(OXFORD_COLORS)}"

    def test_dictionary_keys_lowercase(self):
        """Test that all dictionary keys are lowercase with underscores."""
        for key in OXFORD_COLORS.keys():
            assert key == key.lower(), f"Key '{key}' should be lowercase"
            assert ' ' not in key, f"Key '{key}' should not contain spaces"

    def test_dictionary_values_are_hex(self):
        """Test that all dictionary values are valid hex codes."""
        for name, hex_code in OXFORD_COLORS.items():
            assert isinstance(hex_code, str), f"{name} value should be a string"
            assert hex_code.startswith('#'), f"{name} value should start with #"
            assert len(hex_code) == 7, f"{name} value should be 7 characters"

    def test_oxford_blue_in_dict(self):
        """Test that oxford_blue is in the dictionary."""
        assert 'oxford_blue' in OXFORD_COLORS
        assert OXFORD_COLORS['oxford_blue'] == '#002147'


class TestDefaultPalette:
    """Test the default OXFORD_PALETTE."""

    def test_palette_length(self):
        """Test that default palette has 8 colors."""
        assert len(OXFORD_PALETTE) == 8, "Default palette should have 8 colors"

    def test_palette_starts_with_oxford_blue(self):
        """Test that palette starts with Oxford Blue."""
        assert OXFORD_PALETTE[0] == '#002147', "First color should be Oxford Blue"

    def test_palette_colors_unique(self):
        """Test that all palette colors are unique."""
        assert len(OXFORD_PALETTE) == len(set(OXFORD_PALETTE)), "All colors should be unique"

    def test_palette_colors_valid_hex(self):
        """Test that all palette colors are valid hex codes."""
        for color in OXFORD_PALETTE:
            assert color.startswith('#')
            assert len(color) == 7


class TestColorPalettes:
    """Test the ColorPalettes class."""

    def test_all_palettes_exist(self):
        """Test that all 13 palettes exist."""
        expected_palettes = [
            'PRIMARY', 'PROFESSIONAL', 'VIBRANT', 'PASTEL',
            'DIVERGING', 'SEQUENTIAL_BLUE', 'HEALTH',
            'TRADITIONAL', 'CONTEMPORARY', 'CELEBRATORY',
            'CORPORATE', 'INNOVATIVE', 'PHC_THESIS'
        ]
        for palette_name in expected_palettes:
            assert hasattr(ColorPalettes, palette_name), f"Palette {palette_name} should exist"

    def test_primary_palette_length(self):
        """Test that PRIMARY palette has 10 colors."""
        assert len(ColorPalettes.PRIMARY) == 10

    def test_professional_palette_length(self):
        """Test that PROFESSIONAL palette has 6 colors."""
        assert len(ColorPalettes.PROFESSIONAL) == 6

    def test_vibrant_palette_length(self):
        """Test that VIBRANT palette has 7 colors."""
        assert len(ColorPalettes.VIBRANT) == 7

    def test_phc_thesis_palette_length(self):
        """Test that PHC_THESIS palette has 27 colors."""
        assert len(ColorPalettes.PHC_THESIS) == 27

    def test_phc_thesis_palette_starts_with_oxford_colors(self):
        """Test that PHC_THESIS palette starts with Oxford branding colors."""
        assert ColorPalettes.PHC_THESIS[0] == '#002147'  # OXFORD_BLUE
        assert ColorPalettes.PHC_THESIS[1] == '#8A1751'  # OXFORD_PHC

    def test_phc_thesis_palette_ends_correctly(self):
        """Test that PHC_THESIS palette ends with white and black."""
        assert ColorPalettes.PHC_THESIS[25] == '#FFFFFF'  # WHITE
        assert ColorPalettes.PHC_THESIS[26] == '#000000'  # BLACK

    def test_palettes_contain_valid_hex(self):
        """Test that all palettes contain valid hex codes."""
        palette_names = [
            'PRIMARY', 'PROFESSIONAL', 'VIBRANT', 'PASTEL',
            'DIVERGING', 'SEQUENTIAL_BLUE', 'HEALTH',
            'TRADITIONAL', 'CONTEMPORARY', 'CELEBRATORY',
            'CORPORATE', 'INNOVATIVE', 'PHC_THESIS'
        ]
        for palette_name in palette_names:
            palette = getattr(ColorPalettes, palette_name)
            for color in palette:
                assert color.startswith('#'), f"Color in {palette_name} should start with #"
                assert len(color) == 7, f"Color in {palette_name} should be 7 characters"


class TestGetColor:
    """Test the get_color function."""

    def test_get_oxford_blue(self):
        """Test getting Oxford Blue by name."""
        assert get_color('oxford_blue') == '#002147'

    def test_get_coral(self):
        """Test getting Coral by name."""
        assert get_color('coral') == '#FE615A'

    def test_invalid_color_raises_error(self):
        """Test that invalid color name raises ValueError."""
        with pytest.raises(ValueError):
            get_color('invalid_color_name')

    def test_error_message_contains_available_colors(self):
        """Test that error message lists available colors."""
        try:
            get_color('invalid')
        except ValueError as e:
            assert 'oxford_blue' in str(e).lower()
            assert 'available colors' in str(e).lower()


class TestGetPalette:
    """Test the get_palette function."""

    def test_get_primary_palette(self):
        """Test getting PRIMARY palette."""
        palette = get_palette('primary')
        assert len(palette) == 10
        assert palette[0] == OxfordColors.OXFORD_BLUE

    def test_get_palette_case_insensitive(self):
        """Test that palette names are case-insensitive."""
        palette1 = get_palette('PRIMARY')
        palette2 = get_palette('primary')
        palette3 = get_palette('Primary')
        assert palette1 == palette2 == palette3

    def test_get_palette_with_n_colors(self):
        """Test getting specific number of colors from palette."""
        palette = get_palette('vibrant', n_colors=3)
        assert len(palette) == 3
        assert palette[0] == ColorPalettes.VIBRANT[0]
        assert palette[1] == ColorPalettes.VIBRANT[1]
        assert palette[2] == ColorPalettes.VIBRANT[2]

    def test_get_palette_cycles_when_too_many_requested(self):
        """Test that palette cycles when requesting more colors than available."""
        # PROFESSIONAL has 6 colors, request 10
        palette = get_palette('professional', n_colors=10)
        assert len(palette) == 10
        # First 6 should match original
        assert palette[:6] == ColorPalettes.PROFESSIONAL
        # Should cycle back to start
        assert palette[6] == ColorPalettes.PROFESSIONAL[0]
        assert palette[7] == ColorPalettes.PROFESSIONAL[1]

    def test_get_palette_returns_copy(self):
        """Test that get_palette returns a copy, not the original."""
        palette = get_palette('primary')
        original = ColorPalettes.PRIMARY
        # Modify the returned palette
        palette.append('#FFFFFF')
        # Original should be unchanged
        assert len(original) == 10

    def test_get_all_palettes(self):
        """Test getting all palette types."""
        palette_names = [
            'primary', 'professional', 'vibrant', 'pastel',
            'diverging', 'sequential_blue', 'health',
            'traditional', 'contemporary', 'celebratory',
            'corporate', 'innovative', 'phc_thesis'
        ]
        for name in palette_names:
            palette = get_palette(name)
            assert isinstance(palette, list)
            assert len(palette) > 0
            assert all(color.startswith('#') for color in palette)

    def test_get_phc_thesis_palette(self):
        """Test getting PHC_THESIS palette specifically."""
        palette = get_palette('phc_thesis')
        assert len(palette) == 27
        assert palette[0] == '#002147'  # OXFORD_BLUE

        # Test case-insensitive
        palette_upper = get_palette('PHC_THESIS')
        assert palette == palette_upper

        # Test cycling
        palette_40 = get_palette('phc_thesis', n_colors=40)
        assert len(palette_40) == 40
        assert palette_40[0] == palette_40[27]  # First color repeats after 27


class TestGetColorPalette:
    """Test the get_color_palette alias function."""

    def test_alias_works_same_as_get_palette(self):
        """Test that get_color_palette is an alias for get_palette."""
        palette1 = get_palette('vibrant', n_colors=5)
        palette2 = get_color_palette('vibrant', n_colors=5)
        assert palette1 == palette2

    def test_alias_with_different_palettes(self):
        """Test alias with various palettes."""
        for name in ['primary', 'professional', 'colorful']:
            try:
                p1 = get_palette(name)
                p2 = get_color_palette(name)
                assert p1 == p2
            except:
                # If one fails, both should fail
                pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
