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


def choose_color():
    """Return a nice color

    Function loops through a list of visible, distinguishable colors

    Returns
    -------
    Color
        A nice, visible color
    """
    color = distinguishable_colors[choose_color.current_color]
    choose_color.current_color = (choose_color.current_color + 1) % len(distinguishable_colors)
    return color


choose_color.current_color = 0


class ColorPicker:
    """Descriptor for picking a sensible color when no color is provided by the user"""
    def __set_name__(self, owner, name):
        self.private_name = '_' + name

    def __get__(self, instance, owner):
        return getattr(instance, self.private_name)

    def __set__(self, instance, value):
        if value is None:
            value = choose_color()
        setattr(instance, self.private_name, value)
