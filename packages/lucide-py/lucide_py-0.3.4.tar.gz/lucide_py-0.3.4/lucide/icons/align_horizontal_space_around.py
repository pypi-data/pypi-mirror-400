
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def AlignHorizontalSpaceAround(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-align-horizontal-space-around'], 'items': [{'rect': {'width': '6', 'height': '10', 'x': '9', 'y': '7', 'rx': '2'}}, {'path': {'d': 'M4 22V2'}}, {'path': {'d': 'M20 22V2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
