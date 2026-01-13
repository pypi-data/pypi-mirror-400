
import contextlib
from collections.abc import Generator
from tagflow import tag
from tagflow.tagflow import AttrValue


@contextlib.contextmanager
def IconBase(
    data: dict, **kwargs
) -> Generator[None]:
    defaults = {
        "width": "24",
        "height": "24",
        "viewBox": "0 0 24 24",
        "fill": "none",
        "stroke": "currentColor",
        "stroke_width": "2",
        "stroke_linecap": "round",
        "stroke_linejoin": "round",
    }
    if "classes" in data:
        defaults["classes"] = data.get("classes")
    
    defaults.update(kwargs)

    with tag.svg(**defaults):        
        for item in data["items"]:
            for element_name, element_attrs in item.items():
                with tag(element_name, **element_attrs):
                    pass
    
    yield
