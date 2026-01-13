
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def AlignVerticalSpaceAround(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-align-vertical-space-around'], 'items': [{'rect': {'width': '10', 'height': '6', 'x': '7', 'y': '9', 'rx': '2'}}, {'path': {'d': 'M22 20H2'}}, {'path': {'d': 'M22 4H2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
