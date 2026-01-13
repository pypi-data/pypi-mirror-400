
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def BetweenHorizontalEnd(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-between-horizontal-end'], 'items': [{'rect': {'width': '13', 'height': '7', 'x': '3', 'y': '3', 'rx': '1'}}, {'path': {'d': 'm22 15-3-3 3-3'}}, {'rect': {'width': '13', 'height': '7', 'x': '3', 'y': '14', 'rx': '1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
