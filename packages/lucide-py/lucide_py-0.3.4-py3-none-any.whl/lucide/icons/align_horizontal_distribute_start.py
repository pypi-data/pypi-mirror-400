
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def AlignHorizontalDistributeStart(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-align-horizontal-distribute-start'], 'items': [{'rect': {'width': '6', 'height': '14', 'x': '4', 'y': '5', 'rx': '2'}}, {'rect': {'width': '6', 'height': '10', 'x': '14', 'y': '7', 'rx': '2'}}, {'path': {'d': 'M4 2v20'}}, {'path': {'d': 'M14 2v20'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
