from colour import Color


distinguishable_colors = (
    "#F0A3FF", # Amethyst
    "#0075DC", # Blue
    "#993F00", # Caramel
    "#4C005C", # Damson
    "#191919", # Ebony
    "#005C31", # Forest
    "#2BCE48", # Green
    "#FFCC99", # Honeydew
    "#808080", # Iron
    "#94FFB5", # Jade
    "#8F7C00", # Khaki
    "#9DCC00", # Lime
    "#C20088", # Mallow
    "#003380", # Navy
    "#FFA405", # Orpiment
    "#FFA8BB", # Pink
    "#426600", # Quagmire
    "#FF0010", # Red
    "#5EF1F2", # Sky
    "#00998F", # Turquoise
    "#E0FF66", # Uranium
    "#740AFF", # Violet
    "#990000", # Wine
    "#FFFF80", # Xanthin
    "#FFFF00", # Yellow
    "#FF5005", # Zinnia
)


def select_color():
    """Return a nice color

    Function loops through a list of visible, distinguishable colors

    Returns
    -------
    Color
        A nice, visible color
    """
    color = distinguishable_colors[select_color.current_color]
    select_color.current_color = (select_color.current_color + 1) % len(distinguishable_colors)
    return color


select_color.current_color = 0


def to_color(value, choose=False):
    """Convert input to color

    Parameters
    ----------
    value : Any
        Input that needs to be converted into a color
    choose : bool
        Whether a color should be picked if input was None

    Returns
    -------
    Color
        The converted or selected color
    """
    if choose:
        value = value or select_color()
    if isinstance(value, str):
        if value.lower()[0:3] == "hsl":
            hsl = value[4:-1].replace("%", "").split(",")
            hsl = [float(f) / 100 for f in hsl]
            hsl[0] = hsl[0] * 100
            return Color(hsl=hsl)
        elif value.lower()[0:3] == "rgb":
            rgb = value[4:-1].split(",")
            rgb = [float(f) / 255 for f in rgb]
            return Color(rgb=rgb)
    return Color(value)
