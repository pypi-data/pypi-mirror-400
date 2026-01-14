import os
import json
from jinja2 import Environment, FileSystemLoader

class WebRenderer:
    """
    Renders the execution trace into an interactive HTML file.
    """
    def __init__(self):
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True  # Prevent XSS / HTML injection from code
        )

        
    def render(self, trace, counts, source_code):
        """
        Generates HTML string from trace and source code.
        """
        template = self.env.get_template('view.html.j2')
        
        # Prepare trace data for JSON serialization (list of dicts)
        trace_data = []
        for step in trace:
            trace_data.append({
                'line_number': step.line_number,
                'event': step.event,
                'func_name': step.func_name,
                'stack': step.stack,
                'locals': step.locals,
                'globals': step.globals,
                'stdout': step.stdout,
                'exception': step.exception
            })
            
        code_lines = source_code.splitlines()
        
        return template.render(
            trace_data=trace_data,
            line_counts=counts,
            code_lines=code_lines,
            source_code=source_code
        )
