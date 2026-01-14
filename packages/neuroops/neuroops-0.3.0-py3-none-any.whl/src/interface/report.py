import base64
import os
from datetime import datetime
import json
import matplotlib
# Force headless backend for server-side generation
matplotlib.use('Agg')
from jinja2 import Environment, FileSystemLoader

def generate_report(file_id, context, notes, user_name="Researcher", plot_base64=None):
    """
    Generates a standalone HTML report using Jinja2 templates.
    Safe for headless environments (Agg backend).
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Locate Template
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(current_dir, "templates")
    
    # Setup Jinja2
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("report_template.html")
    
    # Render
    html = template.render(
        file_id=file_id,
        user_name=user_name,
        timestamp=timestamp,
        context_dict=context,
        plot_base64=plot_base64,
        notes=notes
    )
    
    return html
