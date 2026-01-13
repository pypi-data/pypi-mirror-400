
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Nfc(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-nfc'], 'items': [{'path': {'d': 'M6 8.32a7.43 7.43 0 0 1 0 7.36'}}, {'path': {'d': 'M9.46 6.21a11.76 11.76 0 0 1 0 11.58'}}, {'path': {'d': 'M12.91 4.1a15.91 15.91 0 0 1 .01 15.8'}}, {'path': {'d': 'M16.37 2a20.16 20.16 0 0 1 0 20'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
