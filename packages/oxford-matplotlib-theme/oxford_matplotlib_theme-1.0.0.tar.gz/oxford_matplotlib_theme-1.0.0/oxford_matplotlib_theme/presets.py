"""
Oxford Theme Presets
====================
Pre-configured Oxford theme variants for different use cases.
"""

from typing import Dict, Any
from .styles import apply_oxford_theme


# ============================================================================
# PRESET CONFIGURATIONS
# ============================================================================

PRESETS: Dict[str, Dict[str, Any]] = {
    'default': {
        'description': 'Standard Oxford theme for academic papers',
        'style_base': 'seaborn-v0_8-paper',
        'color_cycle': None,
        'font_scale': 1.0,
    },
    'presentation': {
        'description': 'Larger fonts and elements for slides',
        'style_base': 'seaborn-v0_8-paper',
        'color_cycle': None,
        'font_scale': 1.4,
    },
    'print': {
        'description': 'High contrast for printed materials',
        'style_base': 'seaborn-v0_8-paper',
        'color_cycle': ['oxford_blue', 'coral', 'aqua', 'orange', 'vivid_green'],
        'font_scale': 1.0,
    },
    'colorblind': {
        'description': 'Colorblind-friendly palette',
        'style_base': 'seaborn-v0_8-paper',
        'color_cycle': ['oxford_blue', 'orange', 'aqua', 'mauve', 'vivid_green'],
        'font_scale': 1.0,
    },
    'minimal': {
        'description': 'Minimal styling with grid',
        'style_base': 'seaborn-v0_8-whitegrid',
        'color_cycle': ['oxford_blue', 'royal_blue', 'aqua', 'cerulean_blue'],
        'font_scale': 1.0,
    },
    'notebook': {
        'description': 'Optimized for Jupyter notebooks',
        'style_base': 'seaborn-v0_8-notebook',
        'color_cycle': None,
        'font_scale': 1.1,
    },
    'poster': {
        'description': 'Extra large fonts for conference posters',
        'style_base': 'seaborn-v0_8-paper',
        'color_cycle': None,
        'font_scale': 1.8,
    },
}


# ============================================================================
# PRESET FUNCTIONS
# ============================================================================

def apply_preset(preset_name: str) -> None:
    """
    Apply a pre-configured Oxford theme preset.

    Presets are ready-to-use theme configurations optimized for specific
    use cases like presentations, posters, or colorblind-friendly palettes.

    Parameters
    ----------
    preset_name : str
        Name of the preset to apply (case-insensitive). Available presets:
        - 'default': Standard theme for academic papers
        - 'presentation': Larger fonts for slides (font_scale=1.4)
        - 'print': High contrast colors for printing
        - 'colorblind': Accessible palette for colorblind viewers
        - 'minimal': Clean styling with grid background
        - 'notebook': Optimized for Jupyter notebooks
        - 'poster': Extra large fonts for posters (font_scale=1.8)

    Returns
    -------
    None
        Applies preset configuration to matplotlib rcParams

    Raises
    ------
    ValueError
        If preset_name is not found

    Examples
    --------
    Use presentation preset for slides:

    >>> from oxford_matplotlib_theme import apply_preset
    >>> apply_preset('presentation')
    >>> plt.plot([1, 2, 3], [1, 4, 9])

    Use colorblind-friendly palette:

    >>> apply_preset('colorblind')

    Large fonts for conference poster:

    >>> apply_preset('poster')

    See Also
    --------
    list_presets : Display all available presets
    get_preset_config : Get preset configuration dict
    apply_oxford_theme : Apply theme with custom parameters
    """
    preset_name_lower = preset_name.lower()

    if preset_name_lower not in PRESETS:
        available = ', '.join(sorted(PRESETS.keys()))
        raise ValueError(
            f"Preset '{preset_name}' not found. Available presets: {available}"
        )

    config = PRESETS[preset_name_lower]

    # Apply theme with preset configuration
    apply_oxford_theme(
        style_base=config['style_base'],
        color_cycle=config['color_cycle'],
        font_scale=config['font_scale']
    )


def list_presets() -> None:
    """
    Print a formatted table of all available presets.

    Displays preset names and descriptions to help users choose the right
    preset for their needs.

    Returns
    -------
    None
        Prints to stdout

    Examples
    --------
    >>> from oxford_matplotlib_theme import list_presets
    >>> list_presets()
    Available Oxford Theme Presets:
    ===============================
    default       - Standard Oxford theme for academic papers
    presentation  - Larger fonts and elements for slides
    ...

    See Also
    --------
    apply_preset : Apply a preset
    get_preset_config : Get preset configuration
    """
    print("Available Oxford Theme Presets:")
    print("=" * 70)
    print(f"{'Name':<15} {'Description':<55}")
    print("-" * 70)

    for name in sorted(PRESETS.keys()):
        desc = PRESETS[name]['description']
        print(f"{name:<15} {desc:<55}")

    print("=" * 70)
    print("\nUsage: apply_preset('preset_name')")


def get_preset_config(preset_name: str) -> Dict[str, Any]:
    """
    Get the configuration dictionary for a preset.

    Returns a copy of the preset configuration, useful for inspection or
    creating custom variants.

    Parameters
    ----------
    preset_name : str
        Name of the preset (case-insensitive)

    Returns
    -------
    dict
        Configuration dictionary with keys:
        - 'description': str
        - 'style_base': str
        - 'color_cycle': List[str] or None
        - 'font_scale': float

    Raises
    ------
    ValueError
        If preset_name is not found

    Examples
    --------
    >>> from oxford_matplotlib_theme import get_preset_config
    >>> config = get_preset_config('presentation')
    >>> print(config['font_scale'])
    1.4

    >>> # Modify and use as custom preset
    >>> config = get_preset_config('default')
    >>> config['font_scale'] = 1.3
    >>> apply_oxford_theme(**{k: v for k, v in config.items() if k != 'description'})

    See Also
    --------
    apply_preset : Apply a preset
    list_presets : List all presets
    """
    preset_name_lower = preset_name.lower()

    if preset_name_lower not in PRESETS:
        available = ', '.join(sorted(PRESETS.keys()))
        raise ValueError(
            f"Preset '{preset_name}' not found. Available presets: {available}"
        )

    # Return a copy to prevent modification of the original
    return PRESETS[preset_name_lower].copy()
