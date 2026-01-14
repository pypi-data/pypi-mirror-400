from PythonVisualizer.core.executor import Executor
from PythonVisualizer.visualization.web_renderer import WebRenderer
import os

class CodeVisualizer:
    """
    Main entry point for the Python Code Visualizer.
    """
    
    def __init__(self, code: str, inputs: list = None, timeout: float = 10.0, max_steps: int = 10000):
        if not code or not code.strip():
            raise ValueError("Code cannot be empty")
            
        self.code = code
        self.trace = None
        self.executor = Executor(code, inputs=inputs, timeout=timeout, max_steps=max_steps)

        
    def execute(self):
        """
        Executes the code and stores the trace.
        """
        self.trace = self.executor.execute()
        return self.trace
        
    def render(self, format='web', output_file='visualization.html'):
        """
        Renders the captured trace to the specified format.
        """
        if self.trace is None:
            raise RuntimeError("You must call execute() before rendering.")
            
        if format == 'web':
            renderer = WebRenderer()
            # self.trace is now {'steps': ..., 'counts': ...}
            html_content = renderer.render(
                trace=self.trace['steps'], 
                counts=self.trace['counts'],
                source_code=self.code
            )
            
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"Visualization saved to {os.path.abspath(output_file)}")
                return os.path.abspath(output_file)
            else:
                return html_content
        else:
            raise NotImplementedError(f"Format '{format}' not supported yet.")
