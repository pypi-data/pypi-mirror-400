"""
Oxford University Matplotlib Styling
=====================================
Functions to apply Oxford University styling to Matplotlib figures.
"""

import matplotlib.pyplot as plt
from cycler import cycler
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from typing import Optional, List, Tuple

from .colors import OXFORD_PALETTE, OXFORD_COLORS, get_color


# ============================================================================
# THEME APPLICATION FUNCTIONS
# ============================================================================

def apply_oxford_theme(
    style_base: str = 'seaborn-v0_8-paper',
    color_cycle: Optional[List[str]] = None,
    font_scale: float = 1.0
) -> None:
    """
    Apply Oxford University theme to all matplotlib figures globally.

    This function modifies matplotlib's rcParams to apply Oxford University
    branding, including the official color palette, Oxford Blue for axes and
    labels, and Arial/Helvetica fonts.

    Parameters
    ----------
    style_base : str, default='seaborn-v0_8-paper'
        Base matplotlib style to use as foundation. The Oxford theme will
        override specific parameters. Common options:
        - 'seaborn-v0_8-paper': Publication-ready (recommended)
        - 'seaborn-v0_8-notebook': Jupyter notebooks
        - 'seaborn-v0_8-whitegrid': With background grid

    color_cycle : List[str], optional
        Custom color cycle to use. Can be color names (e.g., 'oxford_blue')
        or hex codes (e.g., '#002147'). If None, uses OXFORD_PALETTE
        (8 colors starting with Oxford Blue).

    font_scale : float, default=1.0
        Multiplier for all font sizes. Use >1.0 for larger fonts (e.g., 1.4
        for presentations) or <1.0 for smaller fonts.

    Returns
    -------
    None
        Modifies matplotlib rcParams in place

    Examples
    --------
    Basic usage:

    >>> from oxford_matplotlib_theme import apply_oxford_theme
    >>> apply_oxford_theme()
    >>> plt.plot([1, 2, 3], [1, 4, 9])
    >>> plt.show()

    Presentation mode (larger fonts):

    >>> apply_oxford_theme(font_scale=1.4)

    Custom color cycle:

    >>> apply_oxford_theme(color_cycle=['oxford_blue', 'coral', 'aqua'])

    With grid background:

    >>> apply_oxford_theme(style_base='seaborn-v0_8-whitegrid')

    See Also
    --------
    reset_theme : Restore matplotlib defaults
    oxford_figure : Create pre-styled figure
    """
    # Input validation
    if font_scale <= 0:
        raise ValueError(f"font_scale must be positive, got {font_scale}")

    if color_cycle is not None and len(color_cycle) == 0:
        raise ValueError("color_cycle cannot be empty")

    # Pre-validate all colors before applying theme (to avoid partial application)
    if color_cycle is not None:
        colors = []
        for color in color_cycle:
            if color.startswith('#'):
                colors.append(color)
            else:
                # This will raise ValueError if color is invalid
                colors.append(get_color(color))
    else:
        colors = OXFORD_PALETTE

    # Apply base style first
    plt.style.use(style_base)

    # Build Oxford-specific rcParams
    oxford_rc = {
        # Color cycle for multi-line/multi-series plots
        'axes.prop_cycle': cycler(color=colors),

        # Oxford Blue for all axes, labels, and text
        'axes.labelcolor': OXFORD_COLORS['oxford_blue'],
        'axes.edgecolor': OXFORD_COLORS['oxford_blue'],
        'text.color': OXFORD_COLORS['oxford_blue'],
        'xtick.color': OXFORD_COLORS['oxford_blue'],
        'ytick.color': OXFORD_COLORS['oxford_blue'],

        # Font family (Oxford standard: Arial/Helvetica)
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans', 'sans-serif'],

        # Legend styling
        'legend.frameon': True,
        'legend.framealpha': 1.0,
        'legend.edgecolor': OXFORD_COLORS['oxford_blue'],
        'legend.fancybox': False,

        # Background colors (white for publication)
        'figure.facecolor': 'white',
        'axes.facecolor': 'white',
    }

    # Apply font scaling if requested
    if font_scale != 1.0:
        font_params = [
            'font.size',
            'axes.labelsize',
            'axes.titlesize',
            'xtick.labelsize',
            'ytick.labelsize',
            'legend.fontsize',
            'figure.titlesize',
        ]

        for param in font_params:
            # Only scale numeric values (some might be strings like 'medium')
            current_value = plt.rcParams[param]
            if isinstance(current_value, (int, float)):
                oxford_rc[param] = current_value * font_scale

    # Update matplotlib rcParams
    plt.rcParams.update(oxford_rc)


def reset_theme() -> None:
    """
    Reset matplotlib to default settings, removing Oxford theme.

    This restores matplotlib's default rcParams, undoing any Oxford theme
    customizations.

    Returns
    -------
    None
        Restores matplotlib rcParams to defaults

    Examples
    --------
    >>> from oxford_matplotlib_theme import apply_oxford_theme, reset_theme
    >>> apply_oxford_theme()
    >>> # ... create plots ...
    >>> reset_theme()  # Back to matplotlib defaults
    """
    plt.rcParams.update(plt.rcParamsDefault)


def oxford_figure(
    figsize: Tuple[float, float] = (10, 6),
    style_base: str = 'seaborn-v0_8-paper',
    color_cycle: Optional[List[str]] = None,
    font_scale: float = 1.0,
    **kwargs
) -> Tuple[Figure, Axes]:
    """
    Create a matplotlib figure with Oxford styling applied.

    This is a convenience function that applies the Oxford theme and creates
    a figure in one step. Useful for one-off figures without modifying global
    rcParams.

    Parameters
    ----------
    figsize : Tuple[float, float], default=(10, 6)
        Figure size in inches (width, height).
        Common sizes:
        - (10, 6): Default
        - (7, 5): Two-column journal figure
        - (3.5, 2.5): Single-column journal figure

    style_base : str, default='seaborn-v0_8-paper'
        Base matplotlib style

    color_cycle : List[str], optional
        Custom color cycle (names or hex codes)

    font_scale : float, default=1.0
        Font size multiplier

    **kwargs
        Additional arguments passed to plt.subplots()

    Returns
    -------
    fig : Figure
        Matplotlib Figure object

    ax : Axes
        Matplotlib Axes object (single axes)

    Examples
    --------
    Basic usage:

    >>> from oxford_matplotlib_theme import oxford_figure
    >>> fig, ax = oxford_figure()
    >>> ax.plot([1, 2, 3], [1, 4, 9])
    >>> ax.set_title('My Plot')
    >>> plt.show()

    Journal-ready single-column figure:

    >>> fig, ax = oxford_figure(figsize=(3.5, 2.5))
    >>> ax.plot(x, y)
    >>> fig.savefig('figure.svg', dpi=300, bbox_inches='tight')

    With custom styling:

    >>> fig, ax = oxford_figure(
    ...     figsize=(8, 6),
    ...     color_cycle=['coral', 'aqua', 'oxford_blue'],
    ...     font_scale=1.2
    ... )

    See Also
    --------
    apply_oxford_theme : Apply theme globally to all figures
    """
    # Input validation
    if figsize[0] <= 0 or figsize[1] <= 0:
        raise ValueError(f"figsize dimensions must be positive, got {figsize}")

    # Apply Oxford theme first
    apply_oxford_theme(
        style_base=style_base,
        color_cycle=color_cycle,
        font_scale=font_scale
    )

    # Create figure with specified size
    fig, ax = plt.subplots(figsize=figsize, **kwargs)

    return fig, ax


def get_oxford_rcparams(
    style_base: str = 'seaborn-v0_8-paper',
    color_cycle: Optional[List[str]] = None,
    font_scale: float = 1.0
) -> dict:
    """
    Get Oxford theme rcParams as a dictionary without applying them.

    Useful for inspecting the theme configuration or applying it selectively.

    Parameters
    ----------
    style_base : str, default='seaborn-v0_8-paper'
        Base matplotlib style

    color_cycle : List[str], optional
        Custom color cycle

    font_scale : float, default=1.0
        Font size multiplier

    Returns
    -------
    dict
        Dictionary of rcParams with Oxford theme settings

    Examples
    --------
    >>> from oxford_matplotlib_theme import get_oxford_rcparams
    >>> oxford_params = get_oxford_rcparams()
    >>> print(oxford_params['axes.labelcolor'])
    '#002147'

    >>> # Inspect what the theme will change
    >>> params = get_oxford_rcparams(font_scale=1.5)
    >>> print(params['font.size'])  # Scaled font size

    See Also
    --------
    apply_oxford_theme : Apply theme globally
    """
    # Save current rcParams
    original_params = plt.rcParams.copy()

    # Apply Oxford theme temporarily
    apply_oxford_theme(
        style_base=style_base,
        color_cycle=color_cycle,
        font_scale=font_scale
    )

    # Get the resulting rcParams
    oxford_params = plt.rcParams.copy()

    # Restore original rcParams
    plt.rcParams.update(original_params)

    return dict(oxford_params)
