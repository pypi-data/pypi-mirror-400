
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Tv(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-tv'], 'items': [{'path': {'d': 'm17 2-5 5-5-5'}}, {'rect': {'width': '20', 'height': '15', 'x': '2', 'y': '7', 'rx': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
