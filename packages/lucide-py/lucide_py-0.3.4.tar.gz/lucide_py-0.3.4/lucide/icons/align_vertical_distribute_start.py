
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def AlignVerticalDistributeStart(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-align-vertical-distribute-start'], 'items': [{'rect': {'width': '14', 'height': '6', 'x': '5', 'y': '14', 'rx': '2'}}, {'rect': {'width': '10', 'height': '6', 'x': '7', 'y': '4', 'rx': '2'}}, {'path': {'d': 'M2 14h20'}}, {'path': {'d': 'M2 4h20'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
