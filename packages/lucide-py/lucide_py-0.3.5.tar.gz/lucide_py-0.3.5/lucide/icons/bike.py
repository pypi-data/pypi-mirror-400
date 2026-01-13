
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Bike(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-bike'], 'items': [{'circle': {'cx': '18.5', 'cy': '17.5', 'r': '3.5'}}, {'circle': {'cx': '5.5', 'cy': '17.5', 'r': '3.5'}}, {'circle': {'cx': '15', 'cy': '5', 'r': '1'}}, {'path': {'d': 'M12 17.5V14l-3-3 4-3 2 3h2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
