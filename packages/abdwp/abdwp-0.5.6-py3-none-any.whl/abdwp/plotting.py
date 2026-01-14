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


def draw_field(
    ax,
    add_detail=False,
    base_scale=3.0,
    zorder=-1,
    set_aspect=True,
):
    # field dimensions (in feet)
    base_distance = 90
    mound_distance = 60.5
    base_side = 1.5 * base_scale  # 18 inches, scaled
    base_offset = base_side / np.sqrt(2)  # diagonal offset for rotated square

    # nominal base positions (intersection points)
    first_pos = np.array([base_distance / np.sqrt(2), base_distance / np.sqrt(2)])
    second_pos = np.array([0, base_distance * np.sqrt(2)])
    third_pos = np.array([-base_distance / np.sqrt(2), base_distance / np.sqrt(2)])

    # outfield arc passes through 3 points:
    # left foul pole: (-233, 233), right foul pole: (233, 233), center field: (0, 400)
    # circle center is on y-axis due to symmetry
    foul_x, foul_y, center_y = 233, 233, 400
    outfield_center_y = (foul_x**2 + foul_y**2 - center_y**2) / (2 * (foul_y - center_y))
    outfield_radius = center_y - outfield_center_y
    theta_right = np.arctan2(foul_y - outfield_center_y, foul_x)
    theta_left = np.pi - theta_right
    theta = np.linspace(theta_right, theta_left, 200)
    outfield_x = outfield_radius * np.cos(theta)
    outfield_y = outfield_center_y + outfield_radius * np.sin(theta)

    # infield arc: circle centered at mound with radius 95 feet
    infield_radius = 95
    infield_center_y = mound_distance

    if add_detail:
        # extends from grass line on left to grass line on right
        grass_offset = 3 / np.sqrt(2)  # perpendicular offset for grass lines

        # find intersection of infield arc with left grass line (y = -x - 2*grass_offset)
        # circle: x² + (y - mound_distance)² = 95²
        # substituting y = -x - 2*grass_offset:
        k = 2 * grass_offset + infield_center_y
        # 2x² + 2kx + k² - r² = 0
        x_left_grass = (-k - np.sqrt(2 * infield_radius**2 - k**2)) / 2
        y_left_grass = -x_left_grass - 2 * grass_offset

        # find intersection with right grass line (y = x - 2*grass_offset)
        # substituting y = x - 2*grass_offset:
        # x² + (x - k)² = r²  ->  2x² - 2kx + k² - r² = 0  (same k as left side)
        x_right_grass = (k + np.sqrt(2 * infield_radius**2 - k**2)) / 2
        y_right_grass = x_right_grass - 2 * grass_offset

        theta_left_infield = np.arctan2(y_left_grass - infield_center_y, x_left_grass)
        theta_right_infield = np.arctan2(y_right_grass - infield_center_y, x_right_grass)
        infield_theta = np.linspace(theta_right_infield, theta_left_infield, 200)
        infield_linestyle = "--"
    else:
        # extends from foul line on left to foul line on right
        # left foul line: y = -x, right foul line: y = x
        # circle: x² + (y - mound_distance)² = 95²
        # for y = x: x² + (x - mound_distance)² = 95²
        #   2x² - 2*mound_distance*x + mound_distance² - 95² = 0
        k_foul = infield_center_y
        x_right_foul = (k_foul + np.sqrt(2 * infield_radius**2 - k_foul**2)) / 2
        y_right_foul = x_right_foul
        # for y = -x: x² + (-x - mound_distance)² = 95²
        #   2x² + 2*mound_distance*x + mound_distance² - 95² = 0
        x_left_foul = (-k_foul - np.sqrt(2 * infield_radius**2 - k_foul**2)) / 2
        y_left_foul = -x_left_foul

        theta_left_infield = np.arctan2(y_left_foul - infield_center_y, x_left_foul)
        theta_right_infield = np.arctan2(y_right_foul - infield_center_y, x_right_foul)
        infield_theta = np.linspace(theta_right_infield, theta_left_infield, 200)
        infield_linestyle = "-"

    infield_x = infield_radius * np.cos(infield_theta)
    infield_y = infield_center_y + infield_radius * np.sin(infield_theta)

    # draw base paths from first to second and second to third (always shown)
    ax.plot(
        [first_pos[0], second_pos[0]],
        [first_pos[1], second_pos[1]],
        "k",
        linewidth=0.5,
        zorder=zorder,
    )
    ax.plot(
        [second_pos[0], third_pos[0]],
        [second_pos[1], third_pos[1]],
        "k",
        linewidth=0.5,
        zorder=zorder,
    )

    # draw base paths from home to first and third to home (only in detail mode,
    # since foul lines already cover these in default mode)
    if add_detail:
        ax.plot([0, first_pos[0]], [0, first_pos[1]], "k", linewidth=0.5, zorder=zorder)
        ax.plot([third_pos[0], 0], [third_pos[1], 0], "k", linewidth=0.5, zorder=zorder)

    # home plate: pentagon per MLB rules
    # 12" edges along foul lines, 8.5" vertical sides, 17" front edge
    # point at (0, 0), front edge faces pitcher
    hp_12 = (1.0 / np.sqrt(2)) * base_scale  # 12" at 45° gives this x and y component
    hp_85 = (8.5 / 12) * base_scale  # 8.5 inches in feet
    # zorder for bases/plates should be above the lines
    patch_zorder = zorder + 1

    home_plate = patches.Polygon(
        [
            (0, 0),  # back point
            (hp_12, hp_12),  # after 12" along first base line
            (hp_12, hp_12 + hp_85),  # after 8.5" up
            (-hp_12, hp_12 + hp_85),  # after 17" across
            (-hp_12, hp_12),  # after 8.5" down
        ],
        closed=True,
        facecolor="black",
        edgecolor="black",
        linewidth=0.5,
        zorder=patch_zorder,
    )
    ax.add_patch(home_plate)

    # first base: 18"x18" square, back corner at intersection, entirely in fair territory
    # edges parallel to baselines, extends into fair territory
    first_base = patches.Polygon(
        [
            first_pos,  # corner on foul line extension
            first_pos + np.array([-base_offset, base_offset]),  # toward second
            first_pos + np.array([-2 * base_offset, 0]),  # deepest in fair territory
            first_pos + np.array([-base_offset, -base_offset]),  # on home-first baseline
        ],
        closed=True,
        facecolor="black",
        edgecolor="black",
        linewidth=0.5,
        zorder=patch_zorder,
    )
    ax.add_patch(first_base)

    # second base: centered on intersection, rotated 45°
    second_base = patches.Polygon(
        [
            second_pos + np.array([0, base_offset]),  # toward center field
            second_pos + np.array([base_offset, 0]),  # toward first
            second_pos + np.array([0, -base_offset]),  # toward home
            second_pos + np.array([-base_offset, 0]),  # toward third
        ],
        closed=True,
        facecolor="black",
        edgecolor="black",
        linewidth=0.5,
        zorder=patch_zorder,
    )
    ax.add_patch(second_base)

    # third base: mirror of first base
    third_base = patches.Polygon(
        [
            third_pos,  # corner on foul line extension
            third_pos + np.array([base_offset, base_offset]),  # toward second
            third_pos + np.array([2 * base_offset, 0]),  # deepest in fair territory
            third_pos + np.array([base_offset, -base_offset]),  # on home-third baseline
        ],
        closed=True,
        facecolor="black",
        edgecolor="black",
        linewidth=0.5,
        zorder=patch_zorder,
    )
    ax.add_patch(third_base)

    # pitcher's mound: 18' diameter circle + 24" x 6" plate (only in detail mode)
    if add_detail:
        mound_circle = patches.Circle(
            (0, 59),  # mound center is 59' from home plate
            radius=9,  # 18' diameter = 9' radius
            facecolor="none",
            edgecolor="black",
            linewidth=0.5,
            linestyle="--",
            zorder=zorder,
        )
        ax.add_patch(mound_circle)

        mound_width = 2.0 * base_scale  # 24 inches, scaled
        mound_depth = 0.5 * base_scale  # 6 inches, scaled
        pitchers_plate = patches.Rectangle(
            (-mound_width / 2, mound_distance),  # front edge at 60.5'
            mound_width,
            mound_depth,
            facecolor="white",
            edgecolor="black",
            linewidth=0.5,
            zorder=patch_zorder,
        )
        ax.add_patch(pitchers_plate)

    # draw arcs
    ax.plot(outfield_x, outfield_y, c="k", linewidth=0.5, zorder=zorder)
    ax.plot(infield_x, infield_y, c="k", linewidth=0.5, linestyle=infield_linestyle, zorder=zorder)

    # foul lines from home to foul poles
    ax.plot([0, -foul_x], [0, foul_y], "k", linewidth=0.5, zorder=zorder)
    ax.plot([0, foul_x], [0, foul_y], "k", linewidth=0.5, zorder=zorder)

    # detailed elements: grass lines, home plate circle, base circles, inner diamond
    if not add_detail:
        if set_aspect:
            ax.set_aspect("equal")
        return

    home_circle_radius = 13  # 26' diameter

    # grass line parallel to left foul line, 3' into foul territory
    # from infield arc toward home plate circle
    # find where grass line intersects home circle
    # grass line: y = -x - 2*grass_offset, circle: x² + y² = 13²
    # substituting: x² + (x + 2*grass_offset)² = 169
    # 2x² + 4*grass_offset*x + 4*grass_offset² - 169 = 0
    a_home = 2
    b_home = 4 * grass_offset
    c_home = 4 * grass_offset**2 - home_circle_radius**2
    x_left_home = (-b_home - np.sqrt(b_home**2 - 4 * a_home * c_home)) / (2 * a_home)
    y_left_home = -x_left_home - 2 * grass_offset
    ax.plot(
        [x_left_grass, x_left_home],
        [y_left_grass, y_left_home],
        "k",
        linewidth=0.5,
        linestyle="--",
        zorder=zorder,
    )

    # grass line parallel to right foul line, 3' into foul territory
    # from infield arc toward home plate circle
    # grass line: y = x - 2*grass_offset, circle: x² + y² = 13²
    # substituting: x² + (x - 2*grass_offset)² = 169
    # 2x² - 4*grass_offset*x + 4*grass_offset² - 169 = 0
    b_home_right = -4 * grass_offset
    x_right_home = (-b_home_right + np.sqrt(b_home_right**2 - 4 * a_home * c_home)) / (2 * a_home)
    y_right_home = x_right_home - 2 * grass_offset
    ax.plot(
        [x_right_grass, x_right_home],
        [y_right_grass, y_right_home],
        "k",
        linewidth=0.5,
        linestyle="--",
        zorder=zorder,
    )

    # home plate circle (26' diameter) - three arcs with gaps on both sides of foul lines
    # foul lines intersect circle at (±13/√2, 13/√2)
    foul_circle_x = home_circle_radius / np.sqrt(2)
    theta_home_left_foul = np.arctan2(foul_circle_x, -foul_circle_x)  # left foul line
    theta_home_right_foul = np.arctan2(foul_circle_x, foul_circle_x)  # right foul line
    # grass line intersections (already computed: x_left_home, y_left_home, x_right_home, y_right_home)
    theta_home_left_grass = np.arctan2(y_left_home, x_left_home)
    theta_home_right_grass = np.arctan2(y_right_home, x_right_home)
    # symmetric points on fair territory side of foul lines
    theta_home_right_fair = 2 * theta_home_right_foul - theta_home_right_grass
    theta_home_left_fair = 2 * theta_home_left_foul - theta_home_left_grass

    # home plate circle arcs (with gaps at foul/grass line intersections)
    home_arc_thetas = [
        np.linspace(theta_home_right_fair, theta_home_left_fair, 100),  # top arc
        np.linspace(-np.pi, theta_home_right_grass, 50),  # back right arc
        np.linspace(theta_home_left_grass, np.pi, 50),  # back left arc
    ]
    for theta_arc in home_arc_thetas:
        ax.plot(
            home_circle_radius * np.cos(theta_arc),
            home_circle_radius * np.sin(theta_arc),
            "k",
            linewidth=0.5,
            linestyle="--",
            zorder=zorder,
        )

    # inner diamond corners (3' inside the baselines)
    inner_offset = 3 * np.sqrt(2)  # corners move diagonally inward
    inner_home = np.array([0, inner_offset])
    inner_first = np.array([first_pos[0] - inner_offset, first_pos[1]])
    inner_second = np.array([0, second_pos[1] - inner_offset])
    inner_third = np.array([third_pos[0] + inner_offset, third_pos[1]])

    # helper function: find where a circle intersects a line segment
    def circle_line_intersect(center, radius, p1, p2):
        # returns intersection points as angles relative to circle center
        d = p2 - p1
        f = p1 - center
        a = np.dot(d, d)
        b = 2 * np.dot(f, d)
        c = np.dot(f, f) - radius**2
        disc = b**2 - 4 * a * c
        if disc < 0:
            return []
        disc = np.sqrt(disc)
        t1 = (-b - disc) / (2 * a)
        t2 = (-b + disc) / (2 * a)
        pts = []
        for t in [t1, t2]:
            if 0 <= t <= 1:
                pt = p1 + t * d
                theta = np.arctan2(pt[1] - center[1], pt[0] - center[0])
                pts.append((theta, pt))
        return pts

    # first base circle - arc outside inner diamond (toward right field/foul territory)
    # intersects inner_home-inner_first and inner_first-inner_second edges
    first_int1 = circle_line_intersect(first_pos, home_circle_radius, inner_home, inner_first)
    first_int2 = circle_line_intersect(first_pos, home_circle_radius, inner_first, inner_second)
    if first_int1 and first_int2:
        theta1 = first_int1[0][0]  # toward home
        theta2 = first_int2[0][0]  # toward second
        # go the long way around (through ±π)
        if theta1 < theta2:
            first_circle_theta = np.concatenate(
                [np.linspace(theta1, -np.pi, 50), np.linspace(np.pi, theta2, 50)]
            )
        else:
            first_circle_theta = np.concatenate(
                [np.linspace(theta1, np.pi, 50), np.linspace(-np.pi, theta2, 50)]
            )
        ax.plot(
            first_pos[0] + home_circle_radius * np.cos(first_circle_theta),
            first_pos[1] + home_circle_radius * np.sin(first_circle_theta),
            "k",
            linewidth=0.5,
            linestyle="--",
            zorder=zorder,
        )

    # second base circle - arc outside inner diamond (toward center field)
    # intersects inner_first-inner_second and inner_second-inner_third edges
    second_int1 = circle_line_intersect(second_pos, home_circle_radius, inner_first, inner_second)
    second_int2 = circle_line_intersect(second_pos, home_circle_radius, inner_second, inner_third)
    if second_int1 and second_int2:
        theta1 = second_int1[0][0]  # toward first
        theta2 = second_int2[0][0]  # toward third
        # go the opposite way (through center field, like third base direction)
        second_circle_theta = np.linspace(theta2, theta1, 100)
        ax.plot(
            second_pos[0] + home_circle_radius * np.cos(second_circle_theta),
            second_pos[1] + home_circle_radius * np.sin(second_circle_theta),
            "k",
            linewidth=0.5,
            linestyle="--",
            zorder=zorder,
        )

    # third base circle - arc outside inner diamond (toward left field/foul territory)
    # intersects inner_second-inner_third and inner_third-inner_home edges
    third_int1 = circle_line_intersect(third_pos, home_circle_radius, inner_second, inner_third)
    third_int2 = circle_line_intersect(third_pos, home_circle_radius, inner_third, inner_home)
    if third_int1 and third_int2:
        theta1 = third_int1[0][0]  # toward second
        theta2 = third_int2[0][0]  # toward home
        # go through the left side (negative x, toward foul territory)
        third_circle_theta = np.linspace(theta1, theta2, 100)
        ax.plot(
            third_pos[0] + home_circle_radius * np.cos(third_circle_theta),
            third_pos[1] + home_circle_radius * np.sin(third_circle_theta),
            "k",
            linewidth=0.5,
            linestyle="--",
            zorder=zorder,
        )

    # inner diamond edges - only segments between base circles
    home_pos = np.array([0, 0])
    inner_edges = [
        (home_pos, first_pos, inner_home, inner_first),
        (first_pos, second_pos, inner_first, inner_second),
        (second_pos, third_pos, inner_second, inner_third),
        (third_pos, home_pos, inner_third, inner_home),
    ]
    for center1, center2, edge_p1, edge_p2 in inner_edges:
        int1 = circle_line_intersect(center1, home_circle_radius, edge_p1, edge_p2)
        int2 = circle_line_intersect(center2, home_circle_radius, edge_p1, edge_p2)
        if int1 and int2:
            p1, p2 = int1[0][1], int2[0][1]
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], "k", linewidth=0.5, linestyle="--", zorder=zorder)

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
