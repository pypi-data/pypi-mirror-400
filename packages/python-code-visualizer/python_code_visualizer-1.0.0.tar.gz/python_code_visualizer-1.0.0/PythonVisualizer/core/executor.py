import sys
import io
import contextlib
import threading
from PythonVisualizer.core.parser import CodeParser
from PythonVisualizer.core.tracer import Tracer

class ExecutionTimeout(Exception):
    """Raised when code execution exceeds timeout."""
    pass

class Executor:
    """
    Executes Python code and returns the execution trace.
    """
    
    def __init__(self, code: str, inputs: list = None, timeout: float = 10.0, max_steps: int = 10000):
        self.code = code
        self.inputs = inputs[:] if inputs else []
        self.timeout = timeout
        self.max_steps = max_steps
        self.tracer = None
        
    def execute(self):
        """
        Runs the code securely (limited) and captures the trace.
        """
        # Validate first
        CodeParser.parse(self.code)
        
        # Capture stdout
        stdout_capture = io.StringIO()
        
        # Initialize Tracer with the buffer and step limit
        self.tracer = Tracer(stdout_buffer=stdout_capture, max_steps=self.max_steps)
        
        # Prepare global execution context
        exec_globals = {}
        
        # Mock input function
        def mock_input(prompt=""):
            stdout_capture.write(prompt)
            if self.inputs:
                value = str(self.inputs.pop(0))
            else:
                value = ""
            stdout_capture.write(value + "\n")
            return value

        exec_globals['input'] = mock_input
        
        # Result container for thread
        result = {'error': None}
        
        def run_code():
            try:
                with contextlib.redirect_stdout(stdout_capture):
                    sys.settrace(self.tracer.trace)
                    try:
                        exec(self.code, exec_globals)
                    except Exception as e:
                        print(f"Error: {e}") 
                    finally:
                        sys.settrace(None)
            except Exception as e:
                result['error'] = e
        
        # Run in thread with timeout
        thread = threading.Thread(target=run_code)
        thread.start()
        thread.join(timeout=self.timeout)
        
        if thread.is_alive():
            # Timeout occurred - we can't kill the thread, but we can return what we have
            # In a real sandbox you'd use multiprocessing
            self.tracer.limit_reached = True  # Signal to stop
            thread.join(timeout=1)  # Give it a moment to stop
            # Add a note about timeout
            print("Warning: Execution timed out")
            
        if result['error']:
            raise result['error']
            
        return {
            'steps': self.tracer.get_trace(),
            'counts': self.tracer.line_counts,
            'limit_reached': self.tracer.limit_reached
        }

