
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def HdmiPort(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-hdmi-port'], 'items': [{'path': {'d': 'M22 9a1 1 0 0 0-1-1H3a1 1 0 0 0-1 1v4a1 1 0 0 0 1 1h1l2 2h12l2-2h1a1 1 0 0 0 1-1Z'}}, {'path': {'d': 'M7.5 12h9'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
