
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Logs(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-logs'], 'items': [{'path': {'d': 'M3 5h1'}}, {'path': {'d': 'M3 12h1'}}, {'path': {'d': 'M3 19h1'}}, {'path': {'d': 'M8 5h1'}}, {'path': {'d': 'M8 12h1'}}, {'path': {'d': 'M8 19h1'}}, {'path': {'d': 'M13 5h8'}}, {'path': {'d': 'M13 12h8'}}, {'path': {'d': 'M13 19h8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
