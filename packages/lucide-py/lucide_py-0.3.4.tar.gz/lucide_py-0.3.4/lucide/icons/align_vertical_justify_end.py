
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def AlignVerticalJustifyEnd(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-align-vertical-justify-end'], 'items': [{'rect': {'width': '14', 'height': '6', 'x': '5', 'y': '12', 'rx': '2'}}, {'rect': {'width': '10', 'height': '6', 'x': '7', 'y': '2', 'rx': '2'}}, {'path': {'d': 'M2 22h20'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
