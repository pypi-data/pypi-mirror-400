"""
Tests for Oxford theme export and branding utilities
"""

import pytest
import matplotlib.pyplot as plt
import os
import tempfile
from oxford_matplotlib_theme.utils import (
    add_oxford_branding,
    save_oxford_figure,
    get_journal_preset,
    JOURNAL_PRESETS,
)
from oxford_matplotlib_theme.styles import oxford_figure, reset_theme


class TestAddOxfordBranding:
    """Test the add_oxford_branding function."""

    def setup_method(self):
        """Create test figure before each test."""
        plt.close('all')
        reset_theme()
        self.fig, self.ax = oxford_figure()
        self.ax.plot([1, 2, 3], [1, 4, 9])

    def teardown_method(self):
        """Clean up after each test."""
        plt.close('all')
        reset_theme()

    def test_returns_figure(self):
        """Test that function returns a figure object."""
        result = add_oxford_branding(self.fig, add_watermark=True)
        assert result is not None
        assert result == self.fig  # Should return the same figure

    def test_no_watermark_by_default(self):
        """Test that watermark is not added when add_watermark=False."""
        # Get initial number of text objects
        initial_texts = len(self.fig.texts)

        # Call without watermark
        add_oxford_branding(self.fig, add_watermark=False)

        # Should not add any text
        assert len(self.fig.texts) == initial_texts

    def test_adds_watermark_when_requested(self):
        """Test that watermark is added when add_watermark=True."""
        initial_texts = len(self.fig.texts)

        add_oxford_branding(self.fig, add_watermark=True)

        # Should add one text object
        assert len(self.fig.texts) == initial_texts + 1

    def test_default_watermark_text(self):
        """Test that default watermark text is 'University of Oxford'."""
        add_oxford_branding(self.fig, add_watermark=True)

        # Check the text of the watermark
        watermark = self.fig.texts[-1]  # Last text added
        assert watermark.get_text() == "University of Oxford"

    def test_custom_watermark_text(self):
        """Test adding custom watermark text."""
        custom_text = "Oxford Primary Care - DRAFT"
        add_oxford_branding(self.fig, add_watermark=True, watermark_text=custom_text)

        watermark = self.fig.texts[-1]
        assert watermark.get_text() == custom_text

    def test_watermark_positions(self):
        """Test that all position options work."""
        positions = ['bottom_right', 'bottom_left', 'top_right', 'top_left']

        for position in positions:
            plt.close('all')
            fig, ax = oxford_figure()
            ax.plot([1, 2, 3], [1, 4, 9])

            add_oxford_branding(fig, add_watermark=True, position=position)

            # Should have added watermark
            assert len(fig.texts) > 0

    def test_invalid_position_raises_error(self):
        """Test that invalid position raises ValueError."""
        with pytest.raises(ValueError):
            add_oxford_branding(self.fig, add_watermark=True, position='invalid_position')

    def test_custom_opacity(self):
        """Test setting custom opacity."""
        add_oxford_branding(self.fig, add_watermark=True, opacity=0.3)

        watermark = self.fig.texts[-1]
        assert watermark.get_alpha() == pytest.approx(0.3, rel=0.01)

    def test_custom_fontsize(self):
        """Test setting custom font size."""
        add_oxford_branding(self.fig, add_watermark=True, fontsize=14)

        watermark = self.fig.texts[-1]
        assert watermark.get_fontsize() == 14


class TestSaveOxfordFigure:
    """Test the save_oxford_figure function."""

    def setup_method(self):
        """Create test figure and temporary directory."""
        plt.close('all')
        reset_theme()
        self.fig, self.ax = oxford_figure()
        self.ax.plot([1, 2, 3], [1, 4, 9])
        self.ax.set_title('Test Plot')

        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test files and figures."""
        plt.close('all')
        reset_theme()

        # Remove test files
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_saves_png_file(self):
        """Test saving as PNG."""
        filename = os.path.join(self.temp_dir, 'test.png')
        save_oxford_figure(self.fig, filename, format='png')

        assert os.path.exists(filename)
        assert os.path.getsize(filename) > 0

    def test_saves_svg_file(self):
        """Test saving as SVG."""
        filename = os.path.join(self.temp_dir, 'test.svg')
        save_oxford_figure(self.fig, filename, format='svg')

        assert os.path.exists(filename)
        assert os.path.getsize(filename) > 0

    def test_saves_pdf_file(self):
        """Test saving as PDF."""
        filename = os.path.join(self.temp_dir, 'test.pdf')
        save_oxford_figure(self.fig, filename, format='pdf')

        assert os.path.exists(filename)
        assert os.path.getsize(filename) > 0

    def test_adds_extension_if_missing(self):
        """Test that file extension is added if missing."""
        filename = os.path.join(self.temp_dir, 'test')  # No extension
        save_oxford_figure(self.fig, filename, format='png')

        expected_filename = filename + '.png'
        assert os.path.exists(expected_filename)

    def test_does_not_duplicate_extension(self):
        """Test that extension is not duplicated if already present."""
        filename = os.path.join(self.temp_dir, 'test.png')
        save_oxford_figure(self.fig, filename, format='png')

        # Should create test.png, not test.png.png
        assert os.path.exists(filename)
        assert not os.path.exists(filename + '.png')

    def test_custom_dpi(self):
        """Test saving with custom DPI."""
        filename = os.path.join(self.temp_dir, 'test_300.png')
        save_oxford_figure(self.fig, filename, format='png', dpi=300)

        assert os.path.exists(filename)

        # Higher DPI should result in larger file (generally)
        filename_150 = os.path.join(self.temp_dir, 'test_150.png')
        save_oxford_figure(self.fig, filename_150, format='png', dpi=150)

        size_300 = os.path.getsize(filename)
        size_150 = os.path.getsize(filename_150)
        assert size_300 > size_150

    def test_bbox_inches_parameter(self):
        """Test that bbox_inches parameter is respected."""
        filename = os.path.join(self.temp_dir, 'test_tight.png')
        save_oxford_figure(self.fig, filename, bbox_inches='tight')

        assert os.path.exists(filename)

    def test_additional_kwargs_passed(self):
        """Test that additional kwargs are passed to savefig."""
        filename = os.path.join(self.temp_dir, 'test_kwargs.png')
        # Pass additional parameter
        save_oxford_figure(self.fig, filename, format='png', pad_inches=0.5)

        assert os.path.exists(filename)


class TestJournalPresets:
    """Test journal preset configurations."""

    def test_journal_presets_exist(self):
        """Test that JOURNAL_PRESETS dictionary exists."""
        assert JOURNAL_PRESETS is not None
        assert len(JOURNAL_PRESETS) > 0

    def test_expected_journals(self):
        """Test that expected journals are defined."""
        expected = ['nature', 'nature_double', 'plos', 'bmj', 'lancet']
        for journal in expected:
            assert journal in JOURNAL_PRESETS, f"Journal '{journal}' should be defined"

    def test_all_presets_have_required_keys(self):
        """Test that all journal presets have required keys."""
        required_keys = ['figsize', 'dpi', 'format']
        for journal_name, config in JOURNAL_PRESETS.items():
            for key in required_keys:
                assert key in config, f"Journal '{journal_name}' missing key '{key}'"

    def test_figsize_is_tuple(self):
        """Test that all figsize values are tuples."""
        for journal_name, config in JOURNAL_PRESETS.items():
            figsize = config['figsize']
            assert isinstance(figsize, tuple), f"{journal_name} figsize should be tuple"
            assert len(figsize) == 2, f"{journal_name} figsize should have 2 values"

    def test_dpi_is_positive_integer(self):
        """Test that all DPI values are positive integers."""
        for journal_name, config in JOURNAL_PRESETS.items():
            dpi = config['dpi']
            assert isinstance(dpi, int), f"{journal_name} DPI should be integer"
            assert dpi > 0, f"{journal_name} DPI should be positive"

    def test_format_is_string(self):
        """Test that all format values are strings."""
        for journal_name, config in JOURNAL_PRESETS.items():
            format_value = config['format']
            assert isinstance(format_value, str), f"{journal_name} format should be string"

    def test_nature_preset_values(self):
        """Test Nature journal preset has correct values."""
        nature = JOURNAL_PRESETS['nature']
        assert nature['figsize'] == (3.5, 2.5)
        assert nature['dpi'] == 300
        assert nature['format'] == 'svg'

    def test_plos_preset_values(self):
        """Test PLOS journal preset has correct values."""
        plos = JOURNAL_PRESETS['plos']
        assert plos['figsize'] == (6.83, 5.0)
        assert plos['dpi'] == 300
        assert plos['format'] == 'tiff'


class TestGetJournalPreset:
    """Test the get_journal_preset function."""

    def test_returns_dict(self):
        """Test that function returns a dictionary."""
        preset = get_journal_preset('nature')
        assert isinstance(preset, dict)

    def test_returns_correct_preset(self):
        """Test that correct preset is returned."""
        preset = get_journal_preset('nature')
        assert preset['figsize'] == (3.5, 2.5)

    def test_case_insensitive(self):
        """Test that journal names are case-insensitive."""
        preset1 = get_journal_preset('nature')
        preset2 = get_journal_preset('NATURE')
        preset3 = get_journal_preset('Nature')

        assert preset1 == preset2 == preset3

    def test_all_journals_accessible(self):
        """Test that all journals can be accessed."""
        for journal_name in JOURNAL_PRESETS.keys():
            preset = get_journal_preset(journal_name)
            assert isinstance(preset, dict)
            assert 'figsize' in preset

    def test_invalid_journal_raises_error(self):
        """Test that invalid journal name raises ValueError."""
        with pytest.raises(ValueError):
            get_journal_preset('nonexistent_journal')

    def test_error_message_lists_journals(self):
        """Test that error message lists available journals."""
        try:
            get_journal_preset('invalid')
        except ValueError as e:
            error_msg = str(e).lower()
            assert 'nature' in error_msg

    def test_returns_copy_not_original(self):
        """Test that function returns a copy, not the original."""
        preset = get_journal_preset('nature')

        # Modify the returned preset
        preset['dpi'] = 999

        # Original should be unchanged
        assert JOURNAL_PRESETS['nature']['dpi'] != 999


class TestExportIntegration:
    """Integration tests for complete export workflow."""

    def setup_method(self):
        """Create temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        plt.close('all')
        reset_theme()

    def teardown_method(self):
        """Clean up."""
        plt.close('all')
        reset_theme()
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_complete_workflow_with_branding(self):
        """Test complete workflow: create, brand, save."""
        # Create figure
        fig, ax = oxford_figure()
        ax.plot([1, 2, 3], [1, 4, 9])
        ax.set_title('Test')

        # Add branding
        add_oxford_branding(fig, add_watermark=True)

        # Save
        filename = os.path.join(self.temp_dir, 'branded.png')
        save_oxford_figure(fig, filename)

        # Verify
        assert os.path.exists(filename)
        assert os.path.getsize(filename) > 0

    def test_journal_ready_figure(self):
        """Test creating journal-ready figure."""
        # Get journal preset
        preset = get_journal_preset('nature')

        # Create figure with journal size
        fig, ax = oxford_figure(figsize=preset['figsize'])
        ax.plot([1, 2, 3], [1, 4, 9])

        # Save with journal settings
        filename = os.path.join(self.temp_dir, 'journal')
        save_oxford_figure(
            fig,
            filename,
            format=preset['format'],
            dpi=preset['dpi']
        )

        # Verify
        expected_file = filename + '.' + preset['format']
        assert os.path.exists(expected_file)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
