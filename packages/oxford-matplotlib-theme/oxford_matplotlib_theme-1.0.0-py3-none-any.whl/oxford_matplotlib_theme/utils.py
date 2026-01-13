"""
Oxford Theme Utilities
======================
Utility functions for branding and exporting figures.
"""

from matplotlib.figure import Figure
from typing import Dict, Any, Literal
from .colors import OXFORD_COLORS


# ============================================================================
# PUBLICATION CONSTANTS
# ============================================================================

# Standard DPI for publication-quality figures
PUBLICATION_DPI = 300
PUBLICATION_DPI_HIGH = 600  # For TIFF or high-quality print

# Supported export formats
SUPPORTED_FORMATS = {'png', 'svg', 'pdf', 'eps', 'tiff', 'jpg', 'jpeg', 'ps', 'raw', 'rgba', 'pgf'}


# ============================================================================
# JOURNAL EXPORT PRESETS
# ============================================================================

JOURNAL_PRESETS: Dict[str, Dict[str, Any]] = {
    'nature': {
        'figsize': (3.5, 2.5),
        'dpi': PUBLICATION_DPI,
        'format': 'svg',
    },
    'nature_double': {
        'figsize': (7.0, 5.0),
        'dpi': PUBLICATION_DPI,
        'format': 'svg',
    },
    'plos': {
        'figsize': (6.83, 5.0),
        'dpi': PUBLICATION_DPI,
        'format': 'tiff',
    },
    'bmj': {
        'figsize': (3.27, 2.5),
        'dpi': PUBLICATION_DPI,
        'format': 'eps',
    },
    'lancet': {
        'figsize': (3.27, 2.5),
        'dpi': PUBLICATION_DPI,
        'format': 'tiff',
    },
}


# ============================================================================
# BRANDING FUNCTIONS
# ============================================================================

def add_oxford_branding(
    fig: Figure,
    add_watermark: bool = False,
    watermark_text: str = "University of Oxford",
    position: Literal['bottom_right', 'bottom_left', 'top_right', 'top_left'] = 'bottom_right',
    opacity: float = 0.5,
    fontsize: int = 10,
) -> Figure:
    """
    Add Oxford University branding watermark to a figure.

    Places a semi-transparent text watermark on the figure, typically used
    for drafts or internal presentations to indicate Oxford affiliation.

    Parameters
    ----------
    fig : Figure
        Matplotlib Figure object to add branding to

    add_watermark : bool, default=False
        Whether to add the watermark. If False, returns fig unchanged.

    watermark_text : str, default="University of Oxford"
        Text to display as watermark

    position : {'bottom_right', 'bottom_left', 'top_right', 'top_left'}, default='bottom_right'
        Corner position for the watermark

    opacity : float, default=0.5
        Transparency of watermark (0=invisible, 1=opaque)

    fontsize : int, default=10
        Font size of watermark text

    Returns
    -------
    Figure
        The same figure object (modified in place)

    Examples
    --------
    Add watermark to figure:

    >>> from oxford_matplotlib_theme import oxford_figure, add_oxford_branding
    >>> fig, ax = oxford_figure()
    >>> ax.plot([1, 2, 3], [1, 4, 9])
    >>> add_oxford_branding(fig, add_watermark=True)
    >>> plt.show()

    Custom watermark:

    >>> add_oxford_branding(
    ...     fig,
    ...     add_watermark=True,
    ...     watermark_text="Oxford Primary Care - DRAFT",
    ...     position='top_left',
    ...     opacity=0.3
    ... )

    See Also
    --------
    save_oxford_figure : Save figure with high-quality settings
    """
    if not add_watermark:
        return fig

    # Input validation
    if not 0 <= opacity <= 1:
        raise ValueError(f"opacity must be between 0 and 1, got {opacity}")

    # Position mapping (figure coordinates: 0-1)
    positions = {
        'bottom_right': {'x': 0.98, 'y': 0.02, 'ha': 'right', 'va': 'bottom'},
        'bottom_left': {'x': 0.02, 'y': 0.02, 'ha': 'left', 'va': 'bottom'},
        'top_right': {'x': 0.98, 'y': 0.98, 'ha': 'right', 'va': 'top'},
        'top_left': {'x': 0.02, 'y': 0.98, 'ha': 'left', 'va': 'top'},
    }

    if position not in positions:
        raise ValueError(
            f"Position '{position}' not recognized. Use: {', '.join(positions.keys())}"
        )

    pos = positions[position]

    # Add watermark text using figure coordinates
    fig.text(
        float(pos['x']),  # type: ignore[arg-type]
        float(pos['y']),  # type: ignore[arg-type]
        watermark_text,
        fontsize=fontsize,
        color=OXFORD_COLORS['stone_grey'],
        alpha=opacity,
        ha=pos['ha'],
        va=pos['va'],
        transform=fig.transFigure,
    )

    return fig


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def save_oxford_figure(
    fig: Figure,
    filename: str,
    format: str = 'png',
    dpi: int = 300,
    bbox_inches: str = 'tight',
    **kwargs
) -> None:
    """
    Save matplotlib figure with high-quality publication settings.

    Unlike Plotly's write_image (which requires kaleido/Chrome), this uses
    matplotlib's native savefig for direct export to various formats.

    Parameters
    ----------
    fig : Figure
        Matplotlib Figure object to save

    filename : str
        Output filename. Extension will be added if missing.

    format : str, default='png'
        Output format: 'png', 'svg', 'pdf', 'eps', 'tiff', etc.

    dpi : int, default=300
        Resolution in dots per inch. 300 is standard for publications.
        Use 600 for high-quality print or TIFF format.

    bbox_inches : str, default='tight'
        Bounding box setting. 'tight' removes excess whitespace.

    **kwargs
        Additional arguments passed to fig.savefig()

    Returns
    -------
    None
        Saves file to disk

    Examples
    --------
    Save as PNG (raster, high quality):

    >>> from oxford_matplotlib_theme import oxford_figure, save_oxford_figure
    >>> fig, ax = oxford_figure()
    >>> ax.plot([1, 2, 3], [1, 4, 9])
    >>> save_oxford_figure(fig, 'my_plot.png')

    Save as SVG (vector, editable):

    >>> save_oxford_figure(fig, 'my_plot', format='svg')

    High-resolution TIFF for journal submission:

    >>> save_oxford_figure(fig, 'figure1', format='tiff', dpi=600)

    Save as PDF with custom settings:

    >>> save_oxford_figure(
    ...     fig,
    ...     'figure.pdf',
    ...     format='pdf',
    ...     dpi=300,
    ...     bbox_inches='tight',
    ...     pad_inches=0.1
    ... )

    Notes
    -----
    - PNG: Best for web, presentations, raster format
    - SVG: Best for editing in Illustrator, vector format
    - PDF: Best for LaTeX documents, vector format
    - TIFF: Required by some journals, high DPI recommended
    - EPS: Legacy format for older journals

    No browser or kaleido dependency required (unlike Plotly).

    See Also
    --------
    add_oxford_branding : Add watermark to figure
    get_journal_preset : Get journal-specific settings
    """
    # Input validation
    if dpi <= 0:
        raise ValueError(f"dpi must be positive, got {dpi}")

    if format.lower() not in SUPPORTED_FORMATS:
        raise ValueError(
            f"format '{format}' not recognized. Valid formats: {', '.join(sorted(SUPPORTED_FORMATS))}"
        )

    # Add file extension if not present
    if not filename.lower().endswith(f'.{format.lower()}'):
        filename = f'{filename}.{format}'

    # Save figure with publication settings
    fig.savefig(
        filename,
        format=format,
        dpi=dpi,
        bbox_inches=bbox_inches,
        **kwargs
    )


def get_journal_preset(journal_name: str) -> Dict[str, Any]:
    """
    Get figure size and export settings for specific journals.

    Provides pre-configured settings matching journal requirements for
    Nature, PLOS, BMJ, Lancet, etc.

    Parameters
    ----------
    journal_name : str
        Name of the journal (case-insensitive). Available:
        - 'nature': Nature single-column (3.5 x 2.5 in, SVG)
        - 'nature_double': Nature double-column (7.0 x 5.0 in, SVG)
        - 'plos': PLOS journals (6.83 x 5.0 in, TIFF)
        - 'bmj': BMJ/British Medical Journal (3.27 x 2.5 in, EPS)
        - 'lancet': Lancet (3.27 x 2.5 in, TIFF)

    Returns
    -------
    dict
        Configuration dictionary with keys:
        - 'figsize': Tuple[float, float] - Figure size in inches
        - 'dpi': int - Resolution
        - 'format': str - File format

    Raises
    ------
    ValueError
        If journal_name is not found

    Examples
    --------
    Create Nature-compliant figure:

    >>> from oxford_matplotlib_theme import get_journal_preset
    >>> preset = get_journal_preset('nature')
    >>> fig, ax = plt.subplots(figsize=preset['figsize'])
    >>> ax.plot([1, 2, 3], [1, 4, 9])
    >>> fig.savefig('figure1.svg', dpi=preset['dpi'], bbox_inches='tight')

    Use with oxford_figure:

    >>> preset = get_journal_preset('plos')
    >>> from oxford_matplotlib_theme import oxford_figure, save_oxford_figure
    >>> fig, ax = oxford_figure(figsize=preset['figsize'])
    >>> ax.plot(x, y)
    >>> save_oxford_figure(fig, 'figure', format=preset['format'], dpi=preset['dpi'])

    Notes
    -----
    Journal requirements change over time. Always verify current submission
    guidelines before preparing final figures.

    See Also
    --------
    save_oxford_figure : Save figure with settings
    oxford_figure : Create figure with custom size
    """
    journal_name_lower = journal_name.lower()

    if journal_name_lower not in JOURNAL_PRESETS:
        available = ', '.join(sorted(JOURNAL_PRESETS.keys()))
        raise ValueError(
            f"Journal '{journal_name}' not found. Available: {available}"
        )

    # Return copy to prevent modification
    return JOURNAL_PRESETS[journal_name_lower].copy()
