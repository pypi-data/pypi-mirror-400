
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Twitch(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-twitch'], 'items': [{'path': {'d': 'M21 2H3v16h5v4l4-4h5l4-4V2zm-10 9V7m5 4V7'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
