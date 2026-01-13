
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareAsterisk(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-asterisk'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M12 8v8'}}, {'path': {'d': 'm8.5 14 7-4'}}, {'path': {'d': 'm8.5 10 7 4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
