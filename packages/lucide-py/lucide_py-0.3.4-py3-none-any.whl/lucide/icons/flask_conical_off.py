
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def FlaskConicalOff(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-flask-conical-off'], 'items': [{'path': {'d': 'M10 2v2.343'}}, {'path': {'d': 'M14 2v6.343'}}, {'path': {'d': 'm2 2 20 20'}}, {'path': {'d': 'M20 20a2 2 0 0 1-2 2H6a2 2 0 0 1-1.755-2.96l5.227-9.563'}}, {'path': {'d': 'M6.453 15H15'}}, {'path': {'d': 'M8.5 2h7'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
