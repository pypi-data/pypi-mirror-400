"""
pygradientify - make terminal ui's beautiful.
Made by Sorrow - want an update or more colors? don't be afraid to make a pull request
"""

from typing import Tuple, Callable, List, Dict


class Colors:
    colors: Dict[str, Tuple[Tuple[int, int, int], Tuple[int, int, int]]] = {
        'purple_to_white': ((127, 0, 255), (255, 255, 255)),
        'red_to_blue': ((255, 0, 0), (0, 0, 255)),
        'red_to_white': ((255, 0, 0), (255, 255, 255)),
        'green_to_yellow': ((0, 255, 0), (255, 255, 0)),
        'black_to_white': ((0, 0, 0), (255, 255, 255)),
        'blue_to_cyan': ((0, 0, 255), (0, 255, 255)),
        'orange_to_pink': ((255, 165, 0), (255, 192, 203)),
        'mint': ((194, 255, 182), (255, 255, 255)),
        'red_to_yellow': ((255, 0, 0), (255, 255, 0)),
        'blue_to_green': ((0, 0, 255), (0, 255, 0)),
        'purple_to_blue': ((128, 0, 128), (0, 0, 255)),
        'pink_to_white': ((255, 192, 203), (255, 255, 255)),
        'cyan_to_magenta': ((0, 255, 255), (255, 0, 255)),
        'gray_to_black': ((169, 169, 169), (0, 0, 0)),
        'blue_to_white': ((0, 0, 255), (255, 255, 255)),
        'red_to_green': ((255, 0, 0), (0, 255, 0)),
        'green_to_blue': ((0, 255, 0), (0, 0, 255)),
        'blue_to_yellow': ((0, 0, 255), (255, 255, 0)),
        'yellow_to_cyan': ((255, 255, 0), (0, 255, 255)),
        'magenta_to_red': ((255, 0, 255), (255, 0, 0)),
        'white_to_black': ((255, 255, 255), (0, 0, 0)),
        'mystic': ((207, 188, 254), (182, 48, 220)),
        'ash': ((255, 0, 0), (128, 128, 128)),
    }

    def __init__(self, s: str, e: str) -> None:
        if s not in Colors.colors or e not in Colors.colors:
            raise ValueError('Color gradient not found')

        self.s = s
        self.e = e

    def _inter(self, t: float, s: Tuple[int, int, int], e: Tuple[int, int, int]) -> Tuple[int, int, int]:
        return tuple(int(s[i] + t * (e[i] - s[i])) for i in range(3))

    def _applyg(self, text: str) -> List[Tuple[int, int, int]]:
        gradient = []
        length = len(text)
        for i in range(length):
            t = i / (length - 1)
            ss = Colors.colors[self.s][0]
            ee = Colors.colors[self.e][1]
            color = self._inter(t, ss, ee)
            gradient.append(color)
        return gradient

    def __call__(self, text: str) -> str:
        gc = self._applyg(text)
        return ''.join(
            f'\033[38;2;{color[0]};{color[1]};{color[2]}m{char}\033[0m'
            for char, color in zip(text, gc)
        )

    @classmethod
    def gg(cls, name: str) -> Callable[[str], str]:
        if name not in cls.colors:
            raise AttributeError(f'Gradient not found: {name}')
        return cls(name, name)


for grad in Colors.colors:
    setattr(Colors, grad, Colors.gg(grad))
