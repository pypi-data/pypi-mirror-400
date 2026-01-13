
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Video(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-video'], 'items': [{'path': {'d': 'm16 13 5.223 3.482a.5.5 0 0 0 .777-.416V7.87a.5.5 0 0 0-.752-.432L16 10.5'}}, {'rect': {'x': '2', 'y': '6', 'width': '14', 'height': '12', 'rx': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
