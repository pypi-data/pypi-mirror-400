
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def AlignHorizontalJustifyStart(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-align-horizontal-justify-start'], 'items': [{'rect': {'width': '6', 'height': '14', 'x': '6', 'y': '5', 'rx': '2'}}, {'rect': {'width': '6', 'height': '10', 'x': '16', 'y': '7', 'rx': '2'}}, {'path': {'d': 'M2 2v20'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
