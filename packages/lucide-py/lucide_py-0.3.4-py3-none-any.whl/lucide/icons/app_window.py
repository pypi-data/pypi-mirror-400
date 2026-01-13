
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def AppWindow(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-app-window'], 'items': [{'rect': {'x': '2', 'y': '4', 'width': '20', 'height': '16', 'rx': '2'}}, {'path': {'d': 'M10 4v4'}}, {'path': {'d': 'M2 8h20'}}, {'path': {'d': 'M6 4v4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
