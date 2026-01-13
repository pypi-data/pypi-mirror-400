
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Ungroup(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-ungroup'], 'items': [{'rect': {'width': '8', 'height': '6', 'x': '5', 'y': '4', 'rx': '1'}}, {'rect': {'width': '8', 'height': '6', 'x': '11', 'y': '14', 'rx': '1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
