
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Equal(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-equal'], 'items': [{'line': {'x1': '5', 'x2': '19', 'y1': '9', 'y2': '9'}}, {'line': {'x1': '5', 'x2': '19', 'y1': '15', 'y2': '15'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
