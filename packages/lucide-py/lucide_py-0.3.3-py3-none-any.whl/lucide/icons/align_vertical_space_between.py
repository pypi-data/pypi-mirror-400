
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def AlignVerticalSpaceBetween(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-align-vertical-space-between'], 'items': [{'rect': {'width': '14', 'height': '6', 'x': '5', 'y': '15', 'rx': '2'}}, {'rect': {'width': '10', 'height': '6', 'x': '7', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M2 21h20'}}, {'path': {'d': 'M2 3h20'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
