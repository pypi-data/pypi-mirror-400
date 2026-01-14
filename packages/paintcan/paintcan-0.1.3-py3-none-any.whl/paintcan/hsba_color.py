import random
from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True)
class HSBAColor:
    """
    A color represented by Hue, Saturation, Brightness, and Alpha components.
    All components are floats in the range [0.0, 1.0].
    """
    hue: float
    saturation: float
    brightness: float
    alpha: float

    def __iter__(self):
        """Allows unpacking: h, s, b, a = color"""
        return iter((self.hue, self.saturation, self.brightness, self.alpha))

    def adjust_hue(self, change: float) -> Self:
        """
        Returns a new HSBAColor with the hue adjusted by the given amount.
        The result is wrapped to the [0.0, 1.0] range cyclically.
        Param `change` must be between -1.0 and 1.0.
        """
        if not (-1.0 <= change <= 1.0):
            raise ValueError("Hue adjustment must be between -1.0 and 1.0")

        new_hue = self.hue + change

        if new_hue > 1.0:
            new_hue -= 1.0
        elif new_hue < 0.0:
            new_hue += 1.0

        return HSBAColor(new_hue, self.saturation, self.brightness, self.alpha)

    def complement(self) -> Self:
        """Returns the complementary color (180 degrees reduced hue)."""
        return self.adjust_hue(0.5)

    def adjust_saturation(
        self,
        change: float,
        floor: float = 0.0,
        ceiling: float = 1.0,
        overflow: bool = False,
    ) -> Self:
        """
        Returns a new HSBAColor with adjusted saturation.
        If overflow is True, values outside [floor, ceiling] wrap around.
        If overflow is False, values are clamped.
        """
        new_saturation = self.saturation + change
        new_saturation = self._apply_bounds(
            new_saturation,
            floor,
            ceiling,
            overflow,
        )
        return HSBAColor(self.hue, new_saturation, self.brightness, self.alpha)

    def adjust_brightness(
        self,
        change: float,
        floor: float = 0.0,
        ceiling: float = 1.0,
        overflow: bool = False,
    ) -> Self:
        """
        Returns a new HSBAColor with adjusted brightness.
        """
        new_brightness = self.brightness + change
        new_brightness = self._apply_bounds(
            new_brightness,
            floor,
            ceiling,
            overflow,
        )
        return HSBAColor(self.hue, self.saturation, new_brightness, self.alpha)

    def adjust_alpha(
        self,
        change: float,
        floor: float = 0.0,
        ceiling: float = 1.0,
    ) -> Self:
        """
        Returns a new HSBAColor with adjusted alpha.
        Alpha is always clamped, never overflows.
        """
        new_alpha = self.alpha + change
        if new_alpha > ceiling:
            new_alpha = ceiling
        elif new_alpha < floor:
            new_alpha = floor

        return HSBAColor(self.hue, self.saturation, self.brightness, new_alpha)

    def _apply_bounds(
        self,
        value: float,
        floor: float,
        ceiling: float,
        overflow: bool,
    ) -> float:
        """Helper to apply floor/ceiling logic with optional overflow."""
        if overflow:
            if value > ceiling:
                value -= (ceiling - floor)
            elif value < floor:
                value += (ceiling - floor)
        else:
            if value > ceiling:
                value = ceiling
            elif value < floor:
                value = floor
        return value

    @classmethod
    def random(
        cls,
        saturation_range: tuple[float, float] = (0.0, 1.0),
        brightness_range: tuple[float, float] = (0.0, 1.0),
    ) -> Self:
        """
        Generates a random HSBAColor.
        Hue is always random [0.0, 1.0].
        Alpha is 1.0.
        """
        return cls(
            hue=random.uniform(0.0, 1.0),
            saturation=random.uniform(*saturation_range),
            brightness=random.uniform(*brightness_range),
            alpha=1.0,
        )
