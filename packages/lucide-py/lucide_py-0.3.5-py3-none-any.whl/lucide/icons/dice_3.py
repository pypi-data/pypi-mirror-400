
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Dice3(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-dice-3'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2', 'ry': '2'}}, {'path': {'d': 'M16 8h.01'}}, {'path': {'d': 'M12 12h.01'}}, {'path': {'d': 'M8 16h.01'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
