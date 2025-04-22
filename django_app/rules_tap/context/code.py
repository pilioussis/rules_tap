import inspect
import sys
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from collections import defaultdict, OrderedDict

@dataclass
class FunctionCall:
    """Represents a single function call with its metadata."""
    name: str
    docstring: Optional[str]
    module: str
    call_count: int = 1

class FunctionTracker:
    """A class to track and store function call information."""
    def __init__(self):
        self.calls: Dict[str, FunctionCall] = OrderedDict()
        self._original_trace = None

    def _trace_calls(self, frame: Any, event: str, arg: Any) -> Any:
        """Internal method to trace function calls."""
        if event != 'call':
            return self._trace_calls

        func = frame.f_code
        func_name = func.co_name
        if func_name == '_trace_calls':  # Skip tracking the tracer itself
            return self._trace_calls

        # Get the actual function object
        module = inspect.getmodule(frame)
        if not module:
            return self._trace_calls

        module_name = module.__name__

        # Try to get the function's docstring
        function_obj = None
        # try:
        function_obj = getattr(module, func_name, None)
        # except Exception as e:
            # print(e)
            # pass

        docstring = inspect.getdoc(function_obj) if function_obj else None
        
        # Create unique key for the function
        key = f"{module_name}.{func_name}"
        
        if key in self.calls:
            self.calls[key].call_count += 1
        else:
            self.calls[key] = FunctionCall(
                name=func_name,
                docstring=docstring,
                module=module_name
            )

        return self._trace_calls

    def start_tracking(self):
        """Start tracking function calls."""
        self._original_trace = sys.gettrace()
        sys.settrace(self._trace_calls)

    def stop_tracking(self):
        """Stop tracking function calls and restore original trace function."""
        sys.settrace(self._original_trace)

    def get_results(self) -> Dict[str, FunctionCall]:
        """Return the collected function call data."""
        return dict(self.calls)

@contextmanager
def track_functions():
    """
    A context manager that tracks all function calls and their docstrings within its scope.
    
    Usage:
        with track_functions() as tracker:
            # Your code here
            some_function()
            
        results = tracker.get_results()
        for key, call in results.items():
            print(f"Function: {call.name}")
            print(f"Module: {call.module}")
            print(f"Docstring: {call.docstring}")
            print(f"Called {call.call_count} times")
    """
    tracker = FunctionTracker()
    tracker.start_tracking()
    try:
        yield tracker
    finally:
        tracker.stop_tracking()

def example_function():
    """This is an example function."""
    pass

def another_function():
    """Another function with a docstring."""
    example_function()

with track_functions() as t:
    another_function()
    for k, v in t.get_results().items():
        print(k, v)
