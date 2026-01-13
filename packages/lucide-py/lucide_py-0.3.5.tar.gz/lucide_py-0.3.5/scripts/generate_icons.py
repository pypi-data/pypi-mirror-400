

import os
import xml.etree.ElementTree as ET
import keyword
import shutil

def to_pascal_case(s):
    pascal_cased = ''.join(word.capitalize() for word in s.replace('-', '_').split('_'))
    # If the pascal cased name is a keyword, append an underscore
    if keyword.iskeyword(pascal_cased):
        return pascal_cased + '_'
    return pascal_cased

def create_icon_library():
    icons_dir = 'resources/lucide/icons'
    
    package_root_dir = 'lucide'
    icons_output_dir = os.path.join(package_root_dir, 'icons')

    os.makedirs(icons_output_dir, exist_ok=True)

    # Clean the icons output directory before generating new files
    for f in os.listdir(icons_output_dir):
        file_path = os.path.join(icons_output_dir, f)
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

    # Open both __init__.py files before the loop
    with open(os.path.join(package_root_dir, '__init__.py'), 'w') as f1, \
         open(os.path.join(icons_output_dir, '__init__.py'), 'w') as f_icons_init:
        
        f1.write("# Lucide Icons\n")
        f_icons_init.write("# Lucide Icons Subpackage\n")

        # Write base.py (this can be outside the f1, f_icons_init context if it doesn't need them)
        with open(os.path.join(icons_output_dir, 'base.py'), 'w') as f_base:
            f_base.write("""
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
""")

        for filename in os.listdir(icons_dir):
            if not filename.endswith('.svg'):
                continue

            icon_name = os.path.splitext(filename)[0]
            
            module_name = icon_name.replace('-', '_')
            if keyword.iskeyword(module_name):
                module_name += '_'

            class_name = to_pascal_case(icon_name)

            with open(os.path.join(icons_dir, filename), 'r') as f_svg:
                svg_content = f_svg.read()

            try:
                root = ET.fromstring(svg_content)
                items = []
                for child in root:
                    tag = child.tag.split('}')[-1]
                    items.append({tag: child.attrib})
                
                data = {
                    "classes": [f"lucide lucide-{icon_name}"],
                    "items": items
                }

                f1.write(f"from .icons.{module_name} import {class_name}\n")
                f_icons_init.write(f"from .{module_name} import {class_name}\n")

                with open(os.path.join(icons_output_dir, f"{module_name}.py"), 'w') as f_icon_module:
                    f_icon_module.write(f"""
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def {class_name}(**kwargs) -> Generator[None]:
    data = {data}
    with IconBase(data, **kwargs):
        pass
    yield
""")
            except ET.ParseError:
                print(f"Could not parse {filename}")


if __name__ == '__main__':
    create_icon_library()
