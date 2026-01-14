from .hsba_color import HSBAColor
from .color_scheme import ColorScheme


def print_color(color: HSBAColor, text: str = "  "):
    # Simple HSBA to RGB conversion for demo purposes
    # Source: https://en.wikipedia.org/wiki/HSL_and_HSV#HSV_to_RGB
    h = color.hue * 360
    s = color.saturation
    v = color.brightness

    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c

    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x

    r = int((r + m) * 255)
    g = int((g + m) * 255)
    b = int((b + m) * 255)

    # ANSI escape code for background color
    print(f"\033[48;2;{r};{g};{b}m{text}\033[0m", end=" ")


def print_scheme(name: str, scheme: ColorScheme):
    print(f"{name:<15}: ", end="")
    for color in scheme:
        print_color(color, "      ")
    print(f"  (Theme Hue: {scheme.theme_color.hue:.2f})")


def main():
    # Start with a random bright color
    print("Generating random base color...")
    base = HSBAColor.random(
        saturation_range=(0.7, 1.0),
        brightness_range=(0.8, 1.0),
    )

    print("\nBetterColors Demo")
    print("=================")
    print(f"{'Base Color':<15}: ", end="")
    print_color(base, "      ")
    print("\n")

    print_scheme("Analogous", ColorScheme.from_analogous(base))
    print_scheme("Complementary", ColorScheme.from_complementary(base))
    print_scheme("Triadic", ColorScheme.from_triadic(base))
    print_scheme("Split Compl.", ColorScheme.from_split_complementary(base))
    print_scheme("Monochromatic", ColorScheme.from_monochromatic(base))
    print_scheme("Compound", ColorScheme.from_compound(base))
    print_scheme("Shades", ColorScheme.from_shades(base))
    print_scheme(
        "Accented Analog",
        ColorScheme.from_accented_analogous(base),
    )


if __name__ == "__main__":
    main()
