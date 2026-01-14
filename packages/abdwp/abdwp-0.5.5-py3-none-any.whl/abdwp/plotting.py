import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import importlib.resources
from typing import Optional

# strike zone definitional constants
STRIKE_ZONE_WIDTH_INCHES = 20
STRIKE_ZONE_WIDTH_FEET = STRIKE_ZONE_WIDTH_INCHES / 12
STRIKE_ZONE_HALF_WIDTH = STRIKE_ZONE_WIDTH_FEET / 2

# parameter aliases for draw_strikezone (matplotlib-style)
_STRIKEZONE_ALIASES = {
    "all_zones": ["az"],
    "border_color": ["bc"],
    "border_linewidth": ["blw"],
    "border_alpha": ["ba"],
    "border_zorder": ["bz"],
    "fill": ["f"],
    "fill_color": ["fc"],
    "fill_alpha": ["fa"],
    "fill_zorder": ["fz"],
}


def _normalize_kwargs(kw, alias_mapping):
    """
    Normalize keyword arguments by converting aliases to canonical names.

    Raises TypeError if both an alias and its canonical name are provided.
    """
    if kw is None:
        return {}

    # build reverse mapping: alias -> canonical
    to_canonical = {}
    for canonical, aliases in alias_mapping.items():
        for alias in aliases:
            to_canonical[alias] = canonical

    out = {}
    seen_canonical = {}  # tracks which canonical key was set by which kwarg

    for key, value in kw.items():
        canonical = to_canonical.get(key, key)
        if canonical in seen_canonical:
            raise TypeError(
                f"got multiple values for argument '{canonical}' "
                f"(from '{seen_canonical[canonical]}' and '{key}')"
            )
        out[canonical] = value
        seen_canonical[canonical] = key

    return out


def use_abdwp_style():
    with importlib.resources.path("abdwp.style", "abdwp.mplstyle") as style_path:
        plt.style.use(str(style_path))


def draw_field(ax, show_mound=False, zorder=-1, set_aspect=True):
    # setup
    base_distance = 90
    mound_distance = 60.5
    outfield_radius = 400
    infield_radius = 200

    # coordinates of bases and mound
    home = np.array([0, 0])
    first = np.array([base_distance / np.sqrt(2), base_distance / np.sqrt(2)])
    second = np.array([0, base_distance * np.sqrt(2)])
    third = np.array([-base_distance / np.sqrt(2), base_distance / np.sqrt(2)])
    mound = np.array([0, mound_distance])

    # outfield arc
    theta = np.linspace(np.pi / 4, 3 * np.pi / 4, 200)
    outfield_x = outfield_radius * np.cos(theta)
    outfield_y = outfield_radius * np.sin(theta)
    outfield = np.vstack([outfield_x, outfield_y])

    # infield arc
    infield_x = infield_radius * np.cos(theta)
    infield_y = infield_radius * np.sin(theta)
    infield = np.vstack([infield_x, infield_y])

    # draw base paths
    ax.plot([home[0], first[0]], [home[1], first[1]], "k", zorder=zorder)
    ax.plot([first[0], second[0]], [first[1], second[1]], "k", zorder=zorder)
    ax.plot([second[0], third[0]], [second[1], third[1]], "k", zorder=zorder)
    ax.plot([third[0], home[0]], [third[1], home[1]], "k", zorder=zorder)

    # draw bases
    ax.scatter(*first, color="black", marker="D", s=20, zorder=zorder)
    ax.scatter(*second, color="black", marker="D", s=20, zorder=zorder)
    ax.scatter(*third, color="black", marker="D", s=20, zorder=zorder)

    # draw home plate
    ax.scatter(0, 0, color="black", marker="D", s=20, zorder=zorder)

    # draw mound
    if show_mound:
        ax.scatter(*mound, color="black", marker="_", zorder=zorder)

    # draw outfield arc
    ax.plot(outfield[0], outfield[1], c="k", zorder=zorder)

    # draw infield arc
    ax.plot(infield[0], infield[1], c="k", zorder=zorder)

    # foul lines
    ax.plot([home[0], outfield[0, 0]], [home[1], outfield[1, 0]], "k", zorder=zorder)
    ax.plot([home[0], outfield[0, -1]], [home[1], outfield[1, -1]], "k", zorder=zorder)

    # set equal aspect ratio for proper field proportions
    if set_aspect:
        ax.set_aspect("equal")


def draw_strikezone(
    ax,
    sz_bot: float = 1.5,
    sz_top: float = 3.5,
    sz_left: Optional[float] = None,
    sz_right: Optional[float] = None,
    xlabel: str = "Horizontal Location (Feet)",
    ylabel: str = "Vertical Location (Feet)",
    set_aspect: bool = True,
    **kwargs,
) -> None:
    """
    Draw a strike zone rectangle on the given axes.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to draw on
    sz_bot : float, default 1.5
        Bottom of strike zone in feet
    sz_top : float, default 3.5
        Top of strike zone in feet
    sz_left : float, optional
        Left edge of strike zone in feet (must be used with sz_right)
    sz_right : float, optional
        Right edge of strike zone in feet (must be used with sz_left)
    xlabel : str, default "Horizontal Location (Feet)"
        X-axis label
    ylabel : str, default "Vertical Location (Feet)"
        Y-axis label
    set_aspect : bool, default True
        Whether to set equal aspect ratio
    **kwargs
        Style options (with short aliases in parentheses):

        - all_zones (az): bool, default False
            Whether to draw a 3x3 grid dividing the strike zone into 9 zones
        - border_color (bc): str, default "black"
            Color for the border and grid lines
        - border_linewidth (blw): float, default 0.5
            Width of the rectangle border
        - border_alpha (ba): float, default 1.0
            Transparency of the border and grid lines
        - border_zorder (bz): int, default 999
            Drawing order for the border rectangle
        - fill (f): bool, default True
            Whether to fill the rectangle
        - fill_color (fc): str, default "tab:gray"
            Color for the fill rectangle
        - fill_alpha (fa): float, default 0.2
            Transparency of the fill rectangle
        - fill_zorder (fz): int, default -999
            Drawing order for the fill rectangle

        Additional kwargs are passed to matplotlib.patches.Rectangle.

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If sz_top <= sz_bot or if only one of sz_left/sz_right is provided
    TypeError
        If both an alias and its canonical name are provided (e.g., bc and border_color)
    """
    if sz_top <= sz_bot:
        raise ValueError("sz_top must be greater than sz_bot")

    if (sz_left is not None) != (sz_right is not None):
        raise ValueError("If used, sz_left and sz_right must be supplied together.")

    # normalize aliases (raises TypeError on conflict)
    kwargs = _normalize_kwargs(kwargs, _STRIKEZONE_ALIASES)

    # extract style options with defaults
    all_zones = kwargs.pop("all_zones", False)
    border_color = kwargs.pop("border_color", "black")
    lw = kwargs.pop("border_linewidth", 0.5)
    border_alpha = kwargs.pop("border_alpha", 1.0)
    border_zorder = kwargs.pop("border_zorder", 999)
    fill = kwargs.pop("fill", True)
    fill_color = kwargs.pop("fill_color", "tab:gray")
    fill_alpha = kwargs.pop("fill_alpha", 0.2)
    fill_zorder = kwargs.pop("fill_zorder", -999)

    height = sz_top - sz_bot
    if sz_left is not None and sz_right is not None:
        width = sz_right - sz_left
    else:
        width = STRIKE_ZONE_WIDTH_FEET
        sz_left = -STRIKE_ZONE_HALF_WIDTH

    if fill:
        fill_rect = patches.Rectangle(
            xy=(sz_left, sz_bot),
            width=width,
            height=height,
            facecolor=fill_color,
            edgecolor="none",
            alpha=fill_alpha,
            zorder=fill_zorder,
            **kwargs,
        )
        ax.add_patch(fill_rect)

    border_rect = patches.Rectangle(
        xy=(sz_left, sz_bot),
        width=width,
        height=height,
        facecolor="none",
        edgecolor=border_color,
        linewidth=lw,
        alpha=border_alpha,
        zorder=border_zorder,
        **kwargs,
    )
    ax.add_patch(border_rect)

    if all_zones:
        v_line1_x = sz_left + width / 3
        v_line2_x = sz_left + 2 * width / 3
        h_line1_y = sz_bot + height / 3
        h_line2_y = sz_bot + 2 * height / 3

        # center lines
        center_x = sz_left + width / 2
        center_y = sz_bot + height / 2

        # vertical grid lines within strike zone
        ax.plot(
            [v_line1_x, v_line1_x],
            [sz_bot, sz_top],
            color=border_color,
            linewidth=lw,
            alpha=border_alpha,
            zorder=border_zorder,
        )
        ax.plot(
            [v_line2_x, v_line2_x],
            [sz_bot, sz_top],
            color=border_color,
            linewidth=lw,
            alpha=border_alpha,
            zorder=border_zorder,
        )

        # horizontal grid lines within strike zone
        ax.plot(
            [sz_left, sz_left + width],
            [h_line1_y, h_line1_y],
            color=border_color,
            linewidth=lw,
            alpha=border_alpha,
            zorder=border_zorder,
        )
        ax.plot(
            [sz_left, sz_left + width],
            [h_line2_y, h_line2_y],
            color=border_color,
            linewidth=lw,
            alpha=border_alpha,
            zorder=border_zorder,
        )

        # extended center lines beyond strike zone
        plot_top = 20
        plot_bottom = -20
        plot_left = -20
        plot_right = 20

        # vertical center line extending from top of strike zone to top of plot
        ax.plot(
            [center_x, center_x],
            [sz_top, plot_top],
            color=border_color,
            linewidth=lw,
            alpha=border_alpha,
            zorder=border_zorder,
        )

        # vertical center line extending from bottom of strike zone to bottom of plot
        ax.plot(
            [center_x, center_x],
            [sz_bot, plot_bottom],
            color=border_color,
            linewidth=lw,
            alpha=border_alpha,
            zorder=border_zorder,
        )

        # horizontal center line extending from left edge of strike zone to left of plot
        ax.plot(
            [sz_left, plot_left],
            [center_y, center_y],
            color=border_color,
            linewidth=lw,
            alpha=border_alpha,
            zorder=border_zorder,
        )

        # horizontal center line extending from right edge of strike zone to right of plot
        ax.plot(
            [sz_left + width, plot_right],
            [center_y, center_y],
            color=border_color,
            linewidth=lw,
            alpha=border_alpha,
            zorder=border_zorder,
        )

        # ensure spines are on top of extended lines
        for spine in ax.spines.values():
            spine.set_zorder(border_zorder + 1)

    # set axis labels
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    # set equal aspect ratio for proper strike zone proportions
    if set_aspect:
        ax.set_aspect("equal")


def add_minor_grid_inches(
    ax,
    alpha: Optional[float] = None,
    linewidth: Optional[float] = None,
) -> None:
    """
    Add minor grid lines at each inch for baseball plots (like strikezone) in units feet.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to add minor grid to
    alpha : float, optional
        Transparency of minor grid lines. If None, uses matplotlib default
    linewidth : float, optional
        Line width of minor grid lines. If None, uses matplotlib default
    """
    ax.xaxis.set_minor_locator(plt.MultipleLocator(1 / 12))
    ax.yaxis.set_minor_locator(plt.MultipleLocator(1 / 12))
    minor_grid_kwargs = {}
    if alpha is not None:
        minor_grid_kwargs["alpha"] = alpha
    if linewidth is not None:
        minor_grid_kwargs["linewidth"] = linewidth
    ax.grid(which="minor", **minor_grid_kwargs)


def remove_plot_elements(ax, spines: bool = False) -> None:
    """
    Remove plot elements to show only data, turning off spines, axis labels, and ticks.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to modify
    spines : bool, default False
        Whether to show spines
    """
    # toggle spines visibility
    for spine in ax.spines.values():
        spine.set_visible(spines)

    # turn off axis labels
    ax.set_xlabel("")
    ax.set_ylabel("")

    # turn off ticks and tick labels
    ax.set_xticks([])
    ax.set_yticks([])
