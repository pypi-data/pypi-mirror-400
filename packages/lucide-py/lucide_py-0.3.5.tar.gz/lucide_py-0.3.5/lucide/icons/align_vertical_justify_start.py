
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def AlignVerticalJustifyStart(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-align-vertical-justify-start'], 'items': [{'rect': {'width': '14', 'height': '6', 'x': '5', 'y': '16', 'rx': '2'}}, {'rect': {'width': '10', 'height': '6', 'x': '7', 'y': '6', 'rx': '2'}}, {'path': {'d': 'M2 2h20'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
