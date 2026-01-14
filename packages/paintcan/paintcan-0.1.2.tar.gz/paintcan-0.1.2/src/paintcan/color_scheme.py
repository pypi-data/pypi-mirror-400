from dataclasses import dataclass
from typing import Iterator, Self, Tuple

from .hsba_color import HSBAColor


@dataclass(frozen=True)
class ColorScheme:
    """
    A collection of colors comprising a color scheme.
    Behaves like a read-only sequence of HSBAColor.
    """

    colors: Tuple[HSBAColor, ...]

    def __post_init__(self):
        if not self.colors:
            raise ValueError("ColorScheme colors cannot be empty")

    def __len__(self) -> int:
        return len(self.colors)

    def __getitem__(self, index: int) -> HSBAColor:
        return self.colors[index]

    def __iter__(self) -> Iterator[HSBAColor]:
        return iter(self.colors)

    @property
    def theme_color(self) -> HSBAColor:
        return self.colors[0]

    @classmethod
    def from_analogous(
        cls,
        theme_color: HSBAColor,
        spacing: float = 0.05,
    ) -> Self:
        if not (0.0 <= spacing < 0.2):
            raise ValueError("Spacing must be between 0 and 0.2")

        colors = [theme_color]

        # Color 2
        colors.append(
            theme_color
            .adjust_saturation(-0.05, floor=0.10)
            .adjust_hue(spacing)
            .adjust_brightness(-0.05, floor=0.20)
        )

        # Color 3
        colors.append(
            theme_color
            .adjust_saturation(-0.05, floor=0.10)
            .adjust_hue(spacing * 2)
            .adjust_brightness(0, floor=0.20)
        )

        # Color 4
        colors.append(
            theme_color
            .adjust_saturation(-0.05, floor=0.10)
            .adjust_hue(-spacing)
            .adjust_brightness(-0.05, floor=0.20)
        )

        # Color 5
        colors.append(
            theme_color
            .adjust_saturation(-0.05, floor=0.10)
            .adjust_hue(-(spacing * 2))
            .adjust_brightness(0, floor=0.20)
        )

        return cls(tuple(colors))

    @classmethod
    def from_accented_analogous(
        cls,
        theme_color: HSBAColor,
        spacing: float = 0.05,
    ) -> Self:
        if not (0.0 <= spacing < 0.2):
            raise ValueError("Spacing must be between 0 and 0.2")

        colors = [theme_color]

        # Color 2
        colors.append(
            theme_color
            .adjust_saturation(-0.05, floor=0.10)
            .adjust_hue(spacing)
            .adjust_brightness(-0.05, floor=0.20)
        )

        # Color 3
        colors.append(
            theme_color
            .adjust_saturation(-0.05, floor=0.10)
            .adjust_hue(-spacing)
            .adjust_brightness(-0.05, floor=0.20)
        )

        # Accent 1
        colors.append(
            theme_color
            .adjust_saturation(-0.05, floor=0.10)
            .adjust_hue(spacing * 2)
            .complement()
            .adjust_brightness(0, floor=0.20)
        )

        # Accent 2
        colors.append(
            theme_color
            .adjust_saturation(-0.05, floor=0.10)
            .adjust_hue(-(spacing * 2))
            .complement()
            .adjust_brightness(0, floor=0.20)
        )

        return cls(tuple(colors))

    @classmethod
    def from_complementary(cls, theme_color: HSBAColor) -> Self:
        colors = [theme_color]

        colors.append(
            theme_color
            .adjust_saturation(0.10)
            .adjust_brightness(
                -0.30,
                floor=0.20,
                overflow=True,
            )
        )

        colors.append(
            theme_color
            .adjust_saturation(-0.10)
            .adjust_brightness(0.30)
        )

        colors.append(
            theme_color
            .complement()
            .adjust_saturation(0.20)
            .adjust_brightness(
                -0.30,
                floor=0.20,
                overflow=True,
            )
        )

        colors.append(theme_color.complement())

        return cls(tuple(colors))

    @classmethod
    def from_compound(cls, theme_color: HSBAColor) -> Self:
        colors = [theme_color]

        colors.append(
            theme_color
            .adjust_hue(0.1)
            .adjust_saturation(-0.10, floor=0.10)
            .adjust_brightness(-0.20, floor=0.20)
        )

        colors.append(
            theme_color
            .adjust_hue(0.1)
            .adjust_saturation(
                -0.40,
                floor=0.10,
                ceiling=0.90,
            )
            .adjust_brightness(-0.40, floor=0.20)
        )

        colors.append(
            theme_color
            .adjust_hue(-0.05)
            .complement()
            .adjust_saturation(-0.25, floor=0.10)
            .adjust_brightness(0.05, floor=0.20)
        )

        colors.append(
            theme_color
            .adjust_hue(-0.1)
            .complement()
            .adjust_saturation(0.10, ceiling=0.90)
            .adjust_brightness(-0.20, floor=0.20)
        )

        return cls(tuple(colors))

    @classmethod
    def from_monochromatic(cls, theme_color: HSBAColor) -> Self:
        colors = [theme_color]

        colors.append(
            theme_color.adjust_brightness(
                -0.50,
                floor=0.20,
                overflow=True,
            )
        )

        colors.append(
            theme_color.adjust_saturation(
                -0.30,
                floor=0.10,
                ceiling=0.70,
                overflow=True,
            )
        )

        colors.append(
            theme_color
            .adjust_brightness(
                -0.50,
                floor=0.20,
                overflow=True,
            )
            .adjust_saturation(
                -0.30,
                floor=0.10,
                ceiling=0.70,
                overflow=True,
            )
        )

        colors.append(
            theme_color.adjust_brightness(
                -0.20,
                floor=0.20,
                overflow=True,
            )
        )

        return cls(tuple(colors))

    @classmethod
    def from_shades(cls, theme_color: HSBAColor) -> Self:
        colors = [theme_color]

        colors.append(
            theme_color.adjust_brightness(
                -0.25,
                floor=0.20,
                overflow=True,
            )
        )
        colors.append(
            theme_color.adjust_brightness(
                -0.50,
                floor=0.20,
                overflow=True,
            )
        )
        colors.append(
            theme_color.adjust_brightness(
                -0.75,
                floor=0.20,
                overflow=True,
            )
        )
        colors.append(
            theme_color.adjust_brightness(-0.10, floor=0.20)
        )

        return cls(tuple(colors))

    @classmethod
    def from_split_complementary(
        cls,
        theme_color: HSBAColor,
        spacing: float = 0.05,
    ) -> Self:
        colors = [theme_color]

        colors.append(
            theme_color
            .adjust_saturation(0.10)
            .adjust_brightness(
                -0.30,
                floor=0.20,
                overflow=True,
            )
        )

        colors.append(
            theme_color
            .adjust_saturation(-0.10)
            .adjust_brightness(0.30)
        )

        colors.append(
            theme_color
            .complement()
            .adjust_hue(spacing)
        )

        colors.append(
            theme_color
            .complement()
            .adjust_hue(-spacing)
        )

        return cls(tuple(colors))

    @classmethod
    def from_triadic(cls, theme_color: HSBAColor) -> Self:
        colors = [theme_color]

        colors.append(
            theme_color
            .adjust_saturation(0.10)
            .adjust_brightness(
                -0.30,
                floor=0.20,
                overflow=True,
            )
        )

        colors.append(
            theme_color
            .adjust_hue(0.33)
            .adjust_saturation(-0.10)
        )

        colors.append(
            theme_color
            .adjust_hue(0.66)
            .adjust_saturation(-0.10)
            .adjust_brightness(-0.20)
        )

        colors.append(
            theme_color
            .adjust_hue(0.66)
            .adjust_saturation(-0.05)
            .adjust_brightness(
                -0.30,
                floor=0.40,
                overflow=True,
            )
        )

        return cls(tuple(colors))
