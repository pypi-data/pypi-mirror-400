
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def FlaskRound(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-flask-round'], 'items': [{'path': {'d': 'M10 2v6.292a7 7 0 1 0 4 0V2'}}, {'path': {'d': 'M5 15h14'}}, {'path': {'d': 'M8.5 2h7'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
