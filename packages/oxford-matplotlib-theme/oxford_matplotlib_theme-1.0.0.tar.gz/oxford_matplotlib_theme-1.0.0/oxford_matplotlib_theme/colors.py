"""
Oxford University Color Definitions
====================================
Official Oxford University brand colors and palettes for Matplotlib visualizations.
Based on Oxford University Brand Guidelines.

Oxford colours: https://communications.admin.ox.ac.uk/communications-resources/visual-identity/identity-guidelines/colours
Oxford theme packs: https://communications.admin.ox.ac.uk/communications-resources/visual-identity/identity-guidelines/theme-packs

Curated by Sami Adnan, 2025
"""

from typing import List, Optional


# ============================================================================
# OXFORD UNIVERSITY OFFICIAL COLORS
# ============================================================================

class OxfordColors:
    """Official Oxford University brand colors."""

    # Primary Color
    OXFORD_BLUE = '#002147'  # RGB(0,33,71) - Pantone 282C

    # PHC Department Accent
    OXFORD_PHC = '#8A1751'  # RGB(138,23,81)

    # Secondary Colors
    MAUVE = '#776885'  # RGB(119,104,133) - Pantone 667C
    PEACH = '#E08D79'  # RGB(224,141,121) - Pantone 4051C
    POTTERS_PINK = '#ED9390'  # RGB(237,147,144) - Pantone 2339C
    DUSK = '#C4A29E'  # RGB(196,162,158) - Pantone 6030C
    LILAC = '#D1BDD5'  # RGB(209,189,213) - Pantone 524C
    SIENNA = '#994636'  # RGB(153,70,54) - Pantone 4036C
    RED = '#BE0F34'  # RGB(190,15,52) - Pantone 187C
    PLUM = '#7F055F'  # RGB(127,5,95) - Pantone 2425C
    CORAL = '#FE615A'  # RGB(254,97,90) - Pantone 178C
    LAVENDER = '#D4CDF4'  # RGB(212,205,244) - Pantone 2635C
    ORANGE = '#FB5607'  # RGB(251,86,7) - Pantone 1655C
    PINK = '#E6007E'  # RGB(230,0,126) - Pantone 2385C
    GREEN = '#426A5A'  # RGB(66,106,90) - Pantone 5545C
    OCEAN_GREY = '#789E9E'  # RGB(120,158,158) - Pantone 2211C
    YELLOW_OCHRE = '#E2C044'  # RGB(226,192,68) - Pantone 4016C
    COOL_GREY = '#E4F0EF'  # RGB(228,240,239) - Pantone 7541C
    SKY_BLUE = '#B9D6F2'  # RGB(185,214,242) - Pantone 277C
    SAGE_GREEN = '#A0AF84'  # RGB(160,175,132) - Pantone 7494C
    VIRIDIAN = '#15616D'  # RGB(21,97,109) - Pantone 5473C
    ROYAL_BLUE = '#1D42A6'  # RGB(29,66,166) - Pantone 2126C
    AQUA = '#00AAB4'  # RGB(0,170,180) - Pantone 7710C
    VIVID_GREEN = '#65E5AE'  # RGB(101,229,174) - Pantone 3385C
    LIME_GREEN = '#95C11F'  # RGB(149,193,31) - Pantone 2292C
    CERULEAN_BLUE = '#49B6FF'  # RGB(73,182,255) - Pantone 292C
    LEMON_YELLOW = '#F7EF66'  # RGB(247,239,102) - Pantone 3935C

    # Neutral Colors
    CHARCOAL = '#211D1C'  # RGB(33,29,28) - Pantone 419C
    ASH_GREY = '#61615F'  # RGB(97,97,95) - Pantone 6215C
    UMBER = '#89827A'  # RGB(137,130,122) - Pantone 403C
    STONE_GREY = '#D9D8D6'  # RGB(217,216,214) - Pantone Cool Gray 1C
    SHELL_GREY = '#F1EEE9'  # RGB(241,238,233) - Pantone Warm Gray 1C
    OFF_WHITE = '#F2F0F0'  # RGB(242,240,240) - Pantone 663C

    # Metallic Colors
    GOLD = '#FFD700'  # RGB(255,215,0) - Pantone 10122C
    SILVER = '#C0C0C0'  # RGB(192,192,192) - Pantone 10103C

    # Thesis Colors (from PHC thesis palette PDFs)
    WHITE = '#FFFFFF'  # RGB(255,255,255) - Thesis background
    BLACK = '#000000'  # RGB(0,0,0) - Thesis text
    THESIS_PURPLE_1 = '#5F4D78'  # RGB(95,77,120) - Thesis primary purple
    BRIGHT_BLUE = '#54ABE7'  # RGB(84,171,231) - Bright blue
    THESIS_PURPLE_2 = '#8A5C9B'  # RGB(138,92,155) - Thesis secondary purple
    SLATE_BLUE_1 = '#57779D'  # RGB(87,119,157) - Slate blue variant 1
    SLATE_BLUE_2 = '#57789E'  # RGB(87,120,158) - Slate blue variant 2
    PERIWINKLE = '#779ECD'  # RGB(119,158,205) - Periwinkle blue
    IRIS = '#6D60B0'  # RGB(109,96,176) - Iris purple
    DEEP_TEAL = '#14616E'  # RGB(20,97,110) - Deep teal
    GOLDEN_YELLOW = '#DFBF45'  # RGB(223,191,69) - Golden yellow
    DUSTY_MAUVE = '#786A83'  # RGB(120,106,131) - Dusty mauve
    WISTERIA = '#9391C8'  # RGB(147,145,200) - Wisteria purple
    POWDER_BLUE = '#C9EEFE'  # RGB(201,238,254) - Powder blue
    GREY_BLUE = '#9FA7C3'  # RGB(159,167,195) - Grey blue
    AMETHYST = '#7E79BC'  # RGB(126,121,188) - Amethyst purple
    NAVY_BLUE = '#06264B'  # RGB(6,38,75) - Navy blue
    SOFT_PURPLE = '#A585B2'  # RGB(165,133,178) - Soft purple
    PALE_GREY = '#E4E7ED'  # RGB(228,231,237) - Pale grey
    HEATHER = '#C5C0DF'  # RGB(197,192,223) - Heather purple
    CORNFLOWER = '#759ECC'  # RGB(117,158,204) - Cornflower blue


# Convenience dictionary for easy access
OXFORD_COLORS = {
    'oxford_blue': OxfordColors.OXFORD_BLUE,
    'oxford_phc': OxfordColors.OXFORD_PHC,
    'mauve': OxfordColors.MAUVE,
    'peach': OxfordColors.PEACH,
    'potters_pink': OxfordColors.POTTERS_PINK,
    'dusk': OxfordColors.DUSK,
    'lilac': OxfordColors.LILAC,
    'sienna': OxfordColors.SIENNA,
    'red': OxfordColors.RED,
    'plum': OxfordColors.PLUM,
    'coral': OxfordColors.CORAL,
    'lavender': OxfordColors.LAVENDER,
    'orange': OxfordColors.ORANGE,
    'pink': OxfordColors.PINK,
    'green': OxfordColors.GREEN,
    'ocean_grey': OxfordColors.OCEAN_GREY,
    'yellow_ochre': OxfordColors.YELLOW_OCHRE,
    'cool_grey': OxfordColors.COOL_GREY,
    'sky_blue': OxfordColors.SKY_BLUE,
    'sage_green': OxfordColors.SAGE_GREEN,
    'viridian': OxfordColors.VIRIDIAN,
    'royal_blue': OxfordColors.ROYAL_BLUE,
    'aqua': OxfordColors.AQUA,
    'vivid_green': OxfordColors.VIVID_GREEN,
    'lime_green': OxfordColors.LIME_GREEN,
    'cerulean_blue': OxfordColors.CERULEAN_BLUE,
    'lemon_yellow': OxfordColors.LEMON_YELLOW,
    'charcoal': OxfordColors.CHARCOAL,
    'ash_grey': OxfordColors.ASH_GREY,
    'umber': OxfordColors.UMBER,
    'stone_grey': OxfordColors.STONE_GREY,
    'shell_grey': OxfordColors.SHELL_GREY,
    'off_white': OxfordColors.OFF_WHITE,
    'gold': OxfordColors.GOLD,
    'silver': OxfordColors.SILVER,
    # Thesis colors
    'white': OxfordColors.WHITE,
    'black': OxfordColors.BLACK,
    'thesis_purple_1': OxfordColors.THESIS_PURPLE_1,
    'bright_blue': OxfordColors.BRIGHT_BLUE,
    'thesis_purple_2': OxfordColors.THESIS_PURPLE_2,
    'slate_blue_1': OxfordColors.SLATE_BLUE_1,
    'slate_blue_2': OxfordColors.SLATE_BLUE_2,
    'periwinkle': OxfordColors.PERIWINKLE,
    'iris': OxfordColors.IRIS,
    'deep_teal': OxfordColors.DEEP_TEAL,
    'golden_yellow': OxfordColors.GOLDEN_YELLOW,
    'dusty_mauve': OxfordColors.DUSTY_MAUVE,
    'wisteria': OxfordColors.WISTERIA,
    'powder_blue': OxfordColors.POWDER_BLUE,
    'grey_blue': OxfordColors.GREY_BLUE,
    'amethyst': OxfordColors.AMETHYST,
    'navy_blue': OxfordColors.NAVY_BLUE,
    'soft_purple': OxfordColors.SOFT_PURPLE,
    'pale_grey': OxfordColors.PALE_GREY,
    'heather': OxfordColors.HEATHER,
    'cornflower': OxfordColors.CORNFLOWER,
}


# Default 8-color cycle for matplotlib (from ideas.md specification)
# This is the default color cycle applied when using the Oxford theme
OXFORD_PALETTE = [
    '#002147',  # oxford_blue - Oxford Blue (primary signature color)
    '#1D42A6',  # royal_blue - Royal Blue
    '#00AAB4',  # aqua - Aqua
    '#FE615A',  # coral - Coral (warm accent)
    '#65E5AE',  # vivid_green - Vivid Green
    '#FB5607',  # orange - Orange (warm accent)
    '#776885',  # mauve - Mauve
    '#49B6FF',  # cerulean_blue - Cerulean Blue
]


# ============================================================================
# COLOR PALETTES
# ============================================================================

class ColorPalettes:
    """Pre-defined color palettes for different visualization needs."""

    # Primary palette - most commonly used colors
    PRIMARY = [
        OxfordColors.OXFORD_BLUE,
        OxfordColors.CORAL,
        OxfordColors.AQUA,
        OxfordColors.YELLOW_OCHRE,
        OxfordColors.PLUM,
        OxfordColors.SAGE_GREEN,
        OxfordColors.ORANGE,
        OxfordColors.SKY_BLUE,
        OxfordColors.PINK,
        OxfordColors.VIRIDIAN,
    ]

    # Professional palette - suitable for business/academic presentations
    PROFESSIONAL = [
        OxfordColors.OXFORD_BLUE,
        OxfordColors.ASH_GREY,
        OxfordColors.GREEN,
        OxfordColors.SIENNA,
        OxfordColors.ROYAL_BLUE,
        OxfordColors.UMBER,
    ]

    # Vibrant palette - for eye-catching visualizations
    VIBRANT = [
        OxfordColors.CORAL,
        OxfordColors.AQUA,
        OxfordColors.ORANGE,
        OxfordColors.PINK,
        OxfordColors.VIVID_GREEN,
        OxfordColors.CERULEAN_BLUE,
        OxfordColors.LEMON_YELLOW,
    ]

    # Pastel palette - for softer visualizations
    PASTEL = [
        OxfordColors.SKY_BLUE,
        OxfordColors.PEACH,
        OxfordColors.LILAC,
        OxfordColors.SAGE_GREEN,
        OxfordColors.POTTERS_PINK,
        OxfordColors.LAVENDER,
        OxfordColors.COOL_GREY,
    ]

    # Diverging palette - for data with a meaningful center point
    DIVERGING = [
        OxfordColors.CORAL,
        OxfordColors.PEACH,
        OxfordColors.STONE_GREY,
        OxfordColors.SKY_BLUE,
        OxfordColors.OXFORD_BLUE,
    ]

    # Sequential palette - for continuous data
    SEQUENTIAL_BLUE = [
        OxfordColors.SKY_BLUE,
        OxfordColors.CERULEAN_BLUE,
        OxfordColors.ROYAL_BLUE,
        OxfordColors.OXFORD_BLUE,
        OxfordColors.CHARCOAL,
    ]

    # Health/Medical palette - suitable for PHC department
    HEALTH = [
        OxfordColors.OXFORD_PHC,
        OxfordColors.PLUM,
        OxfordColors.CORAL,
        OxfordColors.AQUA,
        OxfordColors.SAGE_GREEN,
    ]

    # --- Oxford Theme Packs ---

    # Traditional Theme - Heritage and stability
    TRADITIONAL = [
        OxfordColors.OXFORD_BLUE,
        OxfordColors.RED,
        OxfordColors.GREEN,
        OxfordColors.GOLD,
        OxfordColors.CHARCOAL,
        OxfordColors.STONE_GREY
    ]

    # Contemporary Theme - Modern and clean
    CONTEMPORARY = [
        OxfordColors.MAUVE,
        OxfordColors.PEACH,
        OxfordColors.DUSK,
        OxfordColors.OCEAN_GREY,
        OxfordColors.SIENNA,
        OxfordColors.COOL_GREY
    ]

    # Celebratory Theme - Festive and bright
    CELEBRATORY = [
        OxfordColors.PINK,
        OxfordColors.ORANGE,
        OxfordColors.CORAL,
        OxfordColors.YELLOW_OCHRE,
        OxfordColors.VIVID_GREEN,
        OxfordColors.SKY_BLUE
    ]

    # Corporate Theme - Professional
    CORPORATE = [
        OxfordColors.OXFORD_BLUE,
        OxfordColors.ROYAL_BLUE,
        OxfordColors.CHARCOAL,
        OxfordColors.ASH_GREY,
        OxfordColors.STONE_GREY,
        OxfordColors.OFF_WHITE
    ]

    # Innovative Theme - Forward-looking and tech-focused
    INNOVATIVE = [
        OxfordColors.AQUA,
        OxfordColors.VIVID_GREEN,
        OxfordColors.CERULEAN_BLUE,
        OxfordColors.LIME_GREEN,
        OxfordColors.VIRIDIAN,
        OxfordColors.SKY_BLUE  # Fallback since ELECTRIC_BLUE doesn't exist
    ]

    # PHC Thesis palette - comprehensive 27-color palette for thesis work
    # Combines colors from thesis-colours.pdf, celebratory.pdf, and thesis-extended.pdf
    PHC_THESIS = [
        OxfordColors.OXFORD_BLUE,      # Primary Oxford brand
        OxfordColors.OXFORD_PHC,       # PHC department accent
        OxfordColors.NAVY_BLUE,        # Dark blues
        OxfordColors.DEEP_TEAL,
        OxfordColors.SLATE_BLUE_1,     # Mid blues
        OxfordColors.SLATE_BLUE_2,
        OxfordColors.BRIGHT_BLUE,
        OxfordColors.PERIWINKLE,
        OxfordColors.CORNFLOWER,
        OxfordColors.POWDER_BLUE,      # Light blues
        OxfordColors.THESIS_PURPLE_1,  # Purples
        OxfordColors.THESIS_PURPLE_2,
        OxfordColors.IRIS,
        OxfordColors.AMETHYST,
        OxfordColors.WISTERIA,
        OxfordColors.SOFT_PURPLE,
        OxfordColors.LILAC,
        OxfordColors.LAVENDER,
        OxfordColors.HEATHER,
        OxfordColors.PLUM,             # Deep purple
        OxfordColors.DUSTY_MAUVE,      # Neutral purples
        OxfordColors.GREY_BLUE,
        OxfordColors.ASH_GREY,         # Greys
        OxfordColors.PALE_GREY,
        OxfordColors.GOLDEN_YELLOW,    # Accent
        OxfordColors.WHITE,            # Backgrounds
        OxfordColors.BLACK,
    ]


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_color(name: str) -> str:
    """
    Get a color hex code by name.

    Parameters
    ----------
    name : str
        Name of the color (e.g., 'oxford_blue', 'coral', 'royal_blue').
        Case-insensitive, uses lowercase with underscores internally.

    Returns
    -------
    str
        Hex color code (e.g., '#002147')

    Raises
    ------
    ValueError
        If color name is not found in OXFORD_COLORS dictionary

    Examples
    --------
    >>> get_color('oxford_blue')
    '#002147'
    >>> get_color('Coral')  # case-insensitive
    '#FE615A'
    """
    name_lower = name.lower()
    if name_lower not in OXFORD_COLORS:
        raise ValueError(
            f"Color '{name}' not found. Available colors: {', '.join(sorted(OXFORD_COLORS.keys()))}"
        )
    return OXFORD_COLORS[name_lower]


def get_palette(palette_name: str = 'primary', n_colors: Optional[int] = None) -> List[str]:
    """
    Get a color palette by name.

    Parameters
    ----------
    palette_name : str, default='primary'
        Name of the palette. Case-insensitive. Options:
        - 'primary': General purpose palette (10 colors)
        - 'professional': Business/academic presentations (6 colors)
        - 'vibrant': Eye-catching visualizations (7 colors)
        - 'pastel': Softer visualizations (7 colors)
        - 'diverging': Data with meaningful center point (5 colors)
        - 'sequential_blue': Continuous data (5 colors)
        - 'health': PHC department specific (5 colors)
        - 'traditional': Heritage and stability (6 colors)
        - 'contemporary': Modern and clean (6 colors)
        - 'celebratory': Festive and bright (6 colors)
        - 'corporate': Professional (6 colors)
        - 'innovative': Tech-focused (6 colors)
        - 'phc_thesis': Comprehensive thesis palette (27 colors)

    n_colors : int, optional
        Number of colors to return. If None, returns all colors in palette.
        If more colors requested than available, cycles through the palette.

    Returns
    -------
    List[str]
        List of color hex codes

    Examples
    --------
    >>> colors = get_palette('vibrant', n_colors=5)
    >>> # Use in matplotlib
    >>> for i, color in enumerate(colors):
    ...     ax.plot(x, y[i], color=color)

    >>> # Get full palette
    >>> all_colors = get_palette('traditional')
    """
    palettes = {
        'primary': ColorPalettes.PRIMARY,
        'professional': ColorPalettes.PROFESSIONAL,
        'vibrant': ColorPalettes.VIBRANT,
        'pastel': ColorPalettes.PASTEL,
        'diverging': ColorPalettes.DIVERGING,
        'sequential_blue': ColorPalettes.SEQUENTIAL_BLUE,
        'health': ColorPalettes.HEALTH,
        'traditional': ColorPalettes.TRADITIONAL,
        'contemporary': ColorPalettes.CONTEMPORARY,
        'celebratory': ColorPalettes.CELEBRATORY,
        'corporate': ColorPalettes.CORPORATE,
        'innovative': ColorPalettes.INNOVATIVE,
        'phc_thesis': ColorPalettes.PHC_THESIS,
    }

    # Case-insensitive lookup
    palette_key = palette_name.lower()
    if palette_key not in palettes:
        available = ', '.join(sorted(palettes.keys()))
        raise ValueError(
            f"Palette '{palette_name}' not found. Available palettes: {available}"
        )
    palette = palettes[palette_key]

    # Return copy to prevent mutation
    if n_colors is None:
        return palette.copy()

    # If requesting more colors than available, cycle through
    if n_colors > len(palette):
        return [palette[i % len(palette)] for i in range(n_colors)]

    return palette[:n_colors]


def get_color_palette(palette_name: str = 'primary', n_colors: Optional[int] = None) -> List[str]:
    """
    Alias for get_palette() for compatibility with oxford-plotly-theme.

    Get a color palette by name.

    Parameters
    ----------
    palette_name : str, default='primary'
        Name of the palette (case-insensitive)
    n_colors : int, optional
        Number of colors to return

    Returns
    -------
    List[str]
        List of color hex codes

    See Also
    --------
    get_palette : Main function for getting color palettes
    """
    return get_palette(palette_name, n_colors)
