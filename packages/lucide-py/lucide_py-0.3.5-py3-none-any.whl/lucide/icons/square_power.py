
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquarePower(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-power'], 'items': [{'path': {'d': 'M12 7v4'}}, {'path': {'d': 'M7.998 9.003a5 5 0 1 0 8-.005'}}, {'rect': {'x': '3', 'y': '3', 'width': '18', 'height': '18', 'rx': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
