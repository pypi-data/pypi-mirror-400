
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def FlaskConical(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-flask-conical'], 'items': [{'path': {'d': 'M14 2v6a2 2 0 0 0 .245.96l5.51 10.08A2 2 0 0 1 18 22H6a2 2 0 0 1-1.755-2.96l5.51-10.08A2 2 0 0 0 10 8V2'}}, {'path': {'d': 'M6.453 15h11.094'}}, {'path': {'d': 'M8.5 2h7'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
