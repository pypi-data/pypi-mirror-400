"""
Oxford Matplotlib Theme
=======================
Official Oxford University colors and styling for Matplotlib visualizations.

This package provides a complete theming solution for creating publication-quality
figures with Oxford University branding, including:
- 36 official Oxford University brand colors
- 12 curated color palettes for different visualization needs
- 7 pre-configured theme presets (presentation, poster, colorblind, etc.)
- Journal-specific export settings (Nature, PLOS, BMJ, Lancet)
- Direct SVG/PNG/PDF export (no browser dependencies)

Quick Start
-----------
Basic usage::

    from oxford_matplotlib_theme import apply_oxford_theme
    import matplotlib.pyplot as plt

    # Apply Oxford theme globally
    apply_oxford_theme()

    # Create your plots
    plt.plot([1, 2, 3], [1, 4, 9])
    plt.title('My Oxford Plot')
    plt.show()

Or use the convenience function::

    from oxford_matplotlib_theme import oxford_figure

    fig, ax = oxford_figure()
    ax.plot([1, 2, 3], [1, 4, 9])
    ax.set_title('My Oxford Plot')
    plt.show()

Using presets::

    from oxford_matplotlib_theme import apply_preset

    # Larger fonts for presentations
    apply_preset('presentation')

    # Colorblind-friendly palette
    apply_preset('colorblind')

    # Extra large fonts for posters
    apply_preset('poster')

For more information, see the documentation at:
https://github.com/yourusername/oxford-matplotlib-theme

License
-------
MIT License - Copyright (c) 2025 Sami Adnan

Based on Oxford University Brand Guidelines:
https://communications.admin.ox.ac.uk/communications-resources/visual-identity/identity-guidelines/colours
"""

__version__ = '1.0.0'
__author__ = 'Sami Adnan'
__license__ = 'MIT'

# Import color definitions
from .colors import (
    OxfordColors,
    OXFORD_COLORS,
    OXFORD_PALETTE,
    ColorPalettes,
    get_color,
    get_palette,
    get_color_palette,
)

# Import style functions
from .styles import (
    apply_oxford_theme,
    reset_theme,
    oxford_figure,
    get_oxford_rcparams,
)

# Import preset functions
from .presets import (
    apply_preset,
    list_presets,
    get_preset_config,
    PRESETS,
)

# Import utility functions
from .utils import (
    add_oxford_branding,
    save_oxford_figure,
    get_journal_preset,
    JOURNAL_PRESETS,
    PUBLICATION_DPI,
    PUBLICATION_DPI_HIGH,
    SUPPORTED_FORMATS,
)

# Define public API
__all__ = [
    # Main theme functions
    'apply_oxford_theme',
    'reset_theme',
    'oxford_figure',
    'get_oxford_rcparams',

    # Color access
    'OxfordColors',
    'OXFORD_COLORS',
    'OXFORD_PALETTE',
    'ColorPalettes',
    'get_color',
    'get_palette',
    'get_color_palette',

    # Presets
    'apply_preset',
    'list_presets',
    'get_preset_config',
    'PRESETS',

    # Utilities
    'add_oxford_branding',
    'save_oxford_figure',
    'get_journal_preset',
    'JOURNAL_PRESETS',
    'PUBLICATION_DPI',
    'PUBLICATION_DPI_HIGH',
    'SUPPORTED_FORMATS',
]
