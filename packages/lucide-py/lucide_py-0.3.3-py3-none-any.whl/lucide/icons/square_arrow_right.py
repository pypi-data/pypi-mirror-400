
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareArrowRight(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-arrow-right'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M8 12h8'}}, {'path': {'d': 'm12 16 4-4-4-4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
