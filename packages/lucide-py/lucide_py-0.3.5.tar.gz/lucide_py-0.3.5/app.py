import os
import json
import keyword
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from tagflow import document, tag, text
from collections import defaultdict
import importlib

# Helper function from test_all_icons
def to_pascal_case(s):
    pascal_cased = ''.join(word.capitalize() for word in s.replace('-', '_').split('_'))
    if keyword.iskeyword(pascal_cased):
        return pascal_cased + '_'
    return pascal_cased

app = FastAPI()

def get_categorized_icons():
    icons_dir = 'resources/lucide/icons'
    categorized_icons = defaultdict(list)
    icon_details = {} # Store icon details including categories
    
    for filename in os.listdir(icons_dir):
        if not filename.endswith('.json'):
            continue
            
        icon_name = os.path.splitext(filename)[0]
        
        with open(os.path.join(icons_dir, filename), 'r') as f:
            try:
                data = json.load(f)
                categories = data.get('categories', [])
                icon_details[icon_name] = categories # Store categories for each icon
                for category in categories:
                    categorized_icons[category].append(icon_name)
            except json.JSONDecodeError:
                print(f"Could not decode JSON for {icon_name}")
                continue
                
    return categorized_icons, icon_details

@app.get("/", response_class=HTMLResponse)
async def read_root():
    categorized_icons, icon_details = get_categorized_icons()
    
    with document() as doc:
        with tag("html", class_="bg-gray-100 text-gray-800"):
            with tag("head"):
                with tag("title"):
                    text("Lucide Icons")
                tag("script", src="https://cdn.tailwindcss.com")
                with tag("script"):
                    text("""
                        function filterIcons(selectedCategory) {
                            // Deactivate all category buttons
                            document.querySelectorAll('.category-button').forEach(button => {
                                button.classList.remove('bg-blue-500', 'text-white');
                                button.classList.add('bg-gray-200', 'text-gray-700');
                            });

                            // Activate the selected category button
                            const activeButton = document.getElementById('btn-' + selectedCategory);
                            if (activeButton) {
                                activeButton.classList.add('bg-blue-500', 'text-white');
                                activeButton.classList.remove('bg-gray-200', 'text-gray-700');
                            }

                            document.querySelectorAll('.icon-card').forEach(card => {
                                const categories = card.dataset.categories ? card.dataset.categories.split(',') : [];
                                if (selectedCategory === 'all' || categories.includes(selectedCategory)) {
                                    card.style.display = 'flex';
                                } else {
                                    card.style.display = 'none';
                                }
                            });
                        }

                        function searchIcons() {
                            const query = document.getElementById('search-box').value.toLowerCase();
                            document.querySelectorAll('.icon-card').forEach(card => {
                                const iconName = card.dataset.iconName.toLowerCase();
                                // Only filter visible icons (those not hidden by category filter)
                                if (card.style.display !== 'none') {
                                    if (iconName.includes(query)) {
                                        card.style.display = 'flex';
                                    } else {
                                        card.style.display = 'none';
                                    }
                                }
                            });
                        }

                        // Initial filter to show all icons when page loads
                        document.addEventListener('DOMContentLoaded', () => {
                            filterIcons('all');
                        });
                    """)
            with tag("body", class_="p-8"):
                with tag("div", class_="flex justify-between items-center mb-8"):
                    with tag("h1", class_="text-4xl font-bold"):
                        text("Lucide Icons")
                    with tag("input", id="search-box", type="text", placeholder="Search icons...", class_="px-4 py-2 border rounded-lg", onkeyup="searchIcons()"):
                        pass

                with tag("div", class_="flex flex-wrap gap-2 border-b pb-4 mb-8"): # Changed to flex-wrap for buttons
                    with tag("button", id="btn-all", class_="category-button py-2 px-4 bg-blue-500 text-white rounded-lg focus:outline-none", onclick="filterIcons('all')"):
                        text("All")
                    for category in sorted(categorized_icons.keys()):
                        with tag("button", id=f"btn-{category}", class_="category-button py-2 px-4 bg-gray-200 text-gray-700 rounded-lg focus:outline-none", onclick=f"filterIcons('{category}')"):
                            text(category.capitalize())

                with tag("div", id="all-icons-container", class_="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-4"):
                    # Iterate through all icons, not just categorized ones, to ensure all are displayed
                    # and then filtered by category.
                    all_icon_names = sorted(icon_details.keys())
                    for icon_name in all_icon_names:
                        module_name = icon_name.replace('-', '_')
                        if keyword.iskeyword(module_name):
                            module_name += '_'
                        class_name = to_pascal_case(icon_name)
                        
                        # Get categories for the current icon
                        icon_categories = icon_details.get(icon_name, [])
                        data_categories_attr = ','.join(icon_categories)

                        with tag("div", class_="icon-card flex flex-col items-center justify-center p-4 border rounded-lg shadow-sm bg-white", **{'data-icon-name': icon_name, 'data-categories': data_categories_attr}):
                            try:
                                module = importlib.import_module(f'lucide.icons.{module_name}')
                                icon_class = getattr(module, class_name)
                                with tag("div"):
                                    with icon_class(width="64", height="64"):
                                        pass                                
                                    with tag("p", class_="text-sm mt-2"):
                                      text(icon_name)
                            except (ImportError, AttributeError):
                                with tag("div", class_="text-red-500"):
                                    text(f"Error: {icon_name}")

    return doc.to_html()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
