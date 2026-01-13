
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def TicketCheck(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-ticket-check'], 'items': [{'path': {'d': 'M2 9a3 3 0 0 1 0 6v2a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-2a3 3 0 0 1 0-6V7a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z'}}, {'path': {'d': 'm9 12 2 2 4-4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
