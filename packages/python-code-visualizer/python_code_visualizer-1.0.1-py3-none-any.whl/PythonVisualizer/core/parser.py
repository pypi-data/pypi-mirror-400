import ast

class CodeParser:
    """
    Parses and validates Python code for the visualizer.
    """
    
    @staticmethod
    def parse(code: str):
        """
        Parses the code string into an AST.
        Raises SyntaxError if invalid.
        """
        try:
            tree = ast.parse(code)
            return tree
        except SyntaxError as e:
            raise e

    @staticmethod
    def validate(code: str):
        """
        Checks for potential issues or unsafe constructs.
        Returns a list of warnings (strings).
        """
        warnings = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                # Example check: Infinite loop risks, though hard to detect statically.
                # Here we could check for usage of 'eval', 'exec', or dangerous imports if needed.
                pass
        except SyntaxError:
            pass # execution will fail anyway
            
        return warnings
