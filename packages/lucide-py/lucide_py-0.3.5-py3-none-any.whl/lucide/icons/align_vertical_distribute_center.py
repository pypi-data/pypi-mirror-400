
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def AlignVerticalDistributeCenter(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-align-vertical-distribute-center'], 'items': [{'path': {'d': 'M22 17h-3'}}, {'path': {'d': 'M22 7h-5'}}, {'path': {'d': 'M5 17H2'}}, {'path': {'d': 'M7 7H2'}}, {'rect': {'x': '5', 'y': '14', 'width': '14', 'height': '6', 'rx': '2'}}, {'rect': {'x': '7', 'y': '4', 'width': '10', 'height': '6', 'rx': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
