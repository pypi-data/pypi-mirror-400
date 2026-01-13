
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareRadical(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-radical'], 'items': [{'path': {'d': 'M7 12h2l2 5 2-10h4'}}, {'rect': {'x': '3', 'y': '3', 'width': '18', 'height': '18', 'rx': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
