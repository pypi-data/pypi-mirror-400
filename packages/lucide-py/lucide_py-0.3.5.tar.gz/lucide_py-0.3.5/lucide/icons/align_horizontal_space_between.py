
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def AlignHorizontalSpaceBetween(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-align-horizontal-space-between'], 'items': [{'rect': {'width': '6', 'height': '14', 'x': '3', 'y': '5', 'rx': '2'}}, {'rect': {'width': '6', 'height': '10', 'x': '15', 'y': '7', 'rx': '2'}}, {'path': {'d': 'M3 2v20'}}, {'path': {'d': 'M21 2v20'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
