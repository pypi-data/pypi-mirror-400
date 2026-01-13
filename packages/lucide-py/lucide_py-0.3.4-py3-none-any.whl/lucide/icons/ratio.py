
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Ratio(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-ratio'], 'items': [{'rect': {'width': '12', 'height': '20', 'x': '6', 'y': '2', 'rx': '2'}}, {'rect': {'width': '20', 'height': '12', 'x': '2', 'y': '6', 'rx': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
