
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Film(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-film'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M7 3v18'}}, {'path': {'d': 'M3 7.5h4'}}, {'path': {'d': 'M3 12h18'}}, {'path': {'d': 'M3 16.5h4'}}, {'path': {'d': 'M17 3v18'}}, {'path': {'d': 'M17 7.5h4'}}, {'path': {'d': 'M17 16.5h4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
