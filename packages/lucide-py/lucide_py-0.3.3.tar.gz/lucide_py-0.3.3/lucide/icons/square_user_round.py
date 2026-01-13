
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareUserRound(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-user-round'], 'items': [{'path': {'d': 'M18 21a6 6 0 0 0-12 0'}}, {'circle': {'cx': '12', 'cy': '11', 'r': '4'}}, {'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
