from tagflow import document


kebab_to_pascal = lambda s: ''.join(w.capitalize() for w in s.split('-'))


def get_icon(
        name,
        render: bool = True, 
        **kwargs):
    import lucide
    try:
        if callable(name):
            icon_class = name
        else:
            icon_class = getattr(lucide, name, None)

            if not icon_class:
                icon_class_name = kebab_to_pascal(name)
                icon_class = getattr(lucide, icon_class_name)
            
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
        icon_name_for_error = name if isinstance(name, str) else name.__name__
        print(f"Error rendering lucide icon '{icon_name_for_error}': {e}")

        if render:
            return f'<!-- lucide icon "{icon_name_for_error}" not found -->'    
        else:
            return None
