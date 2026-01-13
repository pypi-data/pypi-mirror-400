from tagflow import document
import icons


kebab_to_pascal = lambda s: ''.join(w.capitalize() for w in s.split('-'))


def get_icon(name: str, render: bool = True, **kwargs):
  
    try:
        icon_class = getattr(icons, name, None)

        if not icon_class:
            icon_class_name = kebab_to_pascal(name)
            icon_class = getattr(icons, icon_class_name)
            
        if not render :
            return icon_class
        
        # Create an icon instance using lucide.create_icon
        with document() as doc:            
            with icon_class(**kwargs):
                pass

        # Return the SVG string
        return doc.to_html() 
    except Exception as e:
        # In case the icon name is invalid or another error occurs
        print(f"Error rendering lucide icon '{name}': {e}")
        return f'<!-- lucide icon "{name}" not found -->'    
