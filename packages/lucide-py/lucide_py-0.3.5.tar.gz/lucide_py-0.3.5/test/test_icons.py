import pytest
from tagflow import (    
    tag,
    text,
    document
)

@pytest.fixture
def doc():
    """Create a new document for testing"""
    with document() as d:
        yield d


def test_basic_document():
    """Test creating a basic document with tags and text"""
    with document() as doc:
        with tag("div"):
            with tag("p"):
                text("Hello World")

    result = doc.to_html(compact=True)
    assert "<div><p>Hello World</p></div>" in result


import os
import importlib
import xml.etree.ElementTree as ET
import keyword
import pytest
from tagflow import (    
    tag,
    html,
    text,
    document
)


@pytest.fixture
def doc():
    """Create a new document for testing"""
    with document() as d:
        yield d


def test_basic_document():
    """Test creating a basic document with tags and text"""
    with document() as doc:
        with tag("div"):
            with tag("p"):
                text("Hello World")

    result = doc.to_html(compact=True)
    assert "<div><p>Hello World</p></div>" in result


def to_pascal_case(s):
    pascal_cased = ''.join(word.capitalize() for word in s.replace('-', '_').split('_'))
    if keyword.iskeyword(pascal_cased):
        return pascal_cased + '_'
    return pascal_cased

def test_all_icons():
    icons_dir = 'resources/lucide/icons'
    for filename in os.listdir(icons_dir):
        if not filename.endswith('.svg'):
            continue

        icon_name = os.path.splitext(filename)[0]
        module_name = icon_name.replace('-', '_')
        if keyword.iskeyword(module_name):
            module_name += '_'
        
        class_name = to_pascal_case(icon_name)

        print(f"Testing {class_name}")

        try:
            module = importlib.import_module(f'lucide.icons.{module_name}')
            icon_class = getattr(module, class_name)
        except (ImportError, AttributeError):
            pytest.fail(f"Could not import {class_name} from lucide.icons.{module_name}")

        with document() as doc:
            with icon_class():
                pass
            rendered_svg_string = doc.to_html(compact=True)
        
        with open(os.path.join(icons_dir, filename), 'r') as f:
            original_svg_string = f.read()

        rendered_root = ET.fromstring(rendered_svg_string)
        original_root = ET.fromstring(original_svg_string)

        rendered_children = list(rendered_root)
        original_children = list(original_root)

        assert len(rendered_children) == len(original_children)

        for rendered_child, original_child in zip(rendered_children, original_children):
            # Compare tags (ignoring namespace)
            assert rendered_child.tag.split('}')[-1] == original_child.tag.split('}')[-1]
            # Compare attributes
            assert rendered_child.attrib == original_child.attrib




