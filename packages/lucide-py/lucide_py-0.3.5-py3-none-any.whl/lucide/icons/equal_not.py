
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def EqualNot(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-equal-not'], 'items': [{'line': {'x1': '5', 'x2': '19', 'y1': '9', 'y2': '9'}}, {'line': {'x1': '5', 'x2': '19', 'y1': '15', 'y2': '15'}}, {'line': {'x1': '19', 'x2': '5', 'y1': '5', 'y2': '19'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
