import random

def get_random_color():
    """Returns a random hex color code."""
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

def rgb_to_hex(r, g, b):
    """Converts RGB values to a Hex color string."""
    return "#{:02x}{:02x}{:02x}".format(r, g, b)

def hex_to_rgb(hex_color):
    """Converts a Hex color string to an RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def moncef_signature():
    """Returns Moncef's signature string."""
    return "Colored by Moncef!"
