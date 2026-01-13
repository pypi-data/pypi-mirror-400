
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Dice2(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-dice-2'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2', 'ry': '2'}}, {'path': {'d': 'M15 9h.01'}}, {'path': {'d': 'M9 15h.01'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
