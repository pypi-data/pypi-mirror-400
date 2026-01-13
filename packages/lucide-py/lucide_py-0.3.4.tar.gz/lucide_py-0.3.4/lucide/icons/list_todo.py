
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ListTodo(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-list-todo'], 'items': [{'path': {'d': 'M13 5h8'}}, {'path': {'d': 'M13 12h8'}}, {'path': {'d': 'M13 19h8'}}, {'path': {'d': 'm3 17 2 2 4-4'}}, {'rect': {'x': '3', 'y': '4', 'width': '6', 'height': '6', 'rx': '1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
