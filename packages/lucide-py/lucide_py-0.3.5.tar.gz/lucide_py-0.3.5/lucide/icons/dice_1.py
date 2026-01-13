
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Dice1(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-dice-1'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2', 'ry': '2'}}, {'path': {'d': 'M12 12h.01'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
