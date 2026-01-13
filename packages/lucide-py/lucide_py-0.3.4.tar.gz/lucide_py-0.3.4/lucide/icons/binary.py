
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Binary(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-binary'], 'items': [{'rect': {'x': '14', 'y': '14', 'width': '4', 'height': '6', 'rx': '2'}}, {'rect': {'x': '6', 'y': '4', 'width': '4', 'height': '6', 'rx': '2'}}, {'path': {'d': 'M6 20h4'}}, {'path': {'d': 'M14 10h4'}}, {'path': {'d': 'M6 14h2v6'}}, {'path': {'d': 'M14 4h2v6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
