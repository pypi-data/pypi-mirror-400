import sys
import linecache
from PythonVisualizer.utils.serializer import Serializer

class ExecutionState:
    def __init__(self, line_number, event, func_name, stack, locals, globals, stdout, exception=None):
        self.line_number = line_number
        self.event = event
        self.func_name = func_name
        self.stack = stack
        self.locals = locals
        self.globals = globals
        self.stdout = stdout       # String content of stdout so far
        self.exception = exception # Dictionary with error details

class Tracer:
    """
    Captures execution logic using sys.settrace.
    """
    def __init__(self, stdout_buffer=None, max_steps=10000):
        self.trace_data = []
        self.serializer = Serializer()
        self.stdout_buffer = stdout_buffer 
        self.line_counts = {} # Map line_no -> count
        self.max_steps = max_steps
        self.step_count = 0
        self.limit_reached = False

    def trace(self, frame, event, arg):
        # Check if limit reached
        if self.limit_reached:
            return None  # Stop tracing
            
        co = frame.f_code
        filename = co.co_filename

        
        if filename != '<string>': 
            return None 

        if event not in ['line', 'return', 'call', 'exception']:
            return self.trace

        line_no = frame.f_lineno
        
        # Track line execution counts
        if event == 'line':
            self.line_counts[line_no] = self.line_counts.get(line_no, 0) + 1

        func_name = co.co_name
        
        # 1. Capture Stack
        stack = []
        f = frame
        while f:
            if f.f_code.co_filename == '<string>':
                stack.append(f.f_code.co_name)
            f = f.f_back
        stack.reverse()

        # 2. Serialize Locals
        local_vars = {}
        for k, v in frame.f_locals.items():
            if k.startswith('__'): continue 
            local_vars[k] = self.serializer.serialize(v)

        # 3. Serialize Globals
        global_vars = {}
        for k, v in frame.f_globals.items():
            if k.startswith('__'): continue 
            if k == 'CodeVisualizer' or k == 'Executor': continue
            if isinstance(v, type(sys)): continue 
            global_vars[k] = self.serializer.serialize(v)

        # 4. Capture Stdout
        current_out = self.stdout_buffer.getvalue() if self.stdout_buffer else ""

        # 5. Capture Exception
        exception_info = None
        if event == 'exception':
            exc_type, exc_value, tb = arg
            exception_info = {
                'type': exc_type.__name__,
                'message': str(exc_value)
            }

        state = ExecutionState(
            line_number=line_no,
            event=event,
            func_name=func_name,
            stack=stack,
            locals=local_vars,
            globals=global_vars,
            stdout=current_out,
            exception=exception_info
        )
        
        self.trace_data.append(state)
        self.step_count += 1
        
        # Check limit
        if self.step_count >= self.max_steps:
            self.limit_reached = True
            return None  # Stop tracing
            
        return self.trace

        
    def get_trace(self):
        return self.trace_data
