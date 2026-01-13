
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Voicemail(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-voicemail'], 'items': [{'circle': {'cx': '6', 'cy': '12', 'r': '4'}}, {'circle': {'cx': '18', 'cy': '12', 'r': '4'}}, {'line': {'x1': '6', 'x2': '18', 'y1': '16', 'y2': '16'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
