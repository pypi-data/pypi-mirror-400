
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquarePilcrow(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-pilcrow'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M12 12H9.5a2.5 2.5 0 0 1 0-5H17'}}, {'path': {'d': 'M12 7v10'}}, {'path': {'d': 'M16 7v10'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
