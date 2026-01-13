
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def AlignHorizontalDistributeCenter(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-align-horizontal-distribute-center'], 'items': [{'rect': {'width': '6', 'height': '14', 'x': '4', 'y': '5', 'rx': '2'}}, {'rect': {'width': '6', 'height': '10', 'x': '14', 'y': '7', 'rx': '2'}}, {'path': {'d': 'M17 22v-5'}}, {'path': {'d': 'M17 7V2'}}, {'path': {'d': 'M7 22v-3'}}, {'path': {'d': 'M7 5V2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
