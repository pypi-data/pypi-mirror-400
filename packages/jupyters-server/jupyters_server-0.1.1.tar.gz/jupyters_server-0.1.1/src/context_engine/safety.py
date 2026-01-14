# Safety Module for ContextEngine
# AST-based destructive command blocking

import ast
import re
from typing import Tuple, List

# Dangerous patterns to block
DANGEROUS_CALLS = {
    'os.remove', 'os.unlink', 'os.rmdir', 'os.removedirs',
    'shutil.rmtree', 'shutil.move', 'shutil.copy',
    'subprocess.call', 'subprocess.run', 'subprocess.Popen',
    'os.system', 'eval', 'exec', 'compile',
    '__import__',
}

DANGEROUS_PATTERNS = [
    r'rm\s+-rf',
    r'DROP\s+TABLE',
    r'DELETE\s+FROM',
    r'TRUNCATE\s+TABLE',
]

class SafetyChecker:
    """Checks code for potentially dangerous operations."""
    
    @classmethod
    def check_code(cls, code: str, force: bool = False) -> Tuple[bool, str]:
        """
        Checks if code is safe to execute.
        
        Returns:
            (is_safe, message)
        """
        if force:
            return True, "Force mode enabled, skipping safety checks."
            
        issues = []
        
        # AST-based check
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    call_name = cls._get_call_name(node)
                    if call_name in DANGEROUS_CALLS:
                        issues.append(f"Dangerous call detected: {call_name}")
        except SyntaxError:
            pass  # Allow code with syntax errors (they'll fail at runtime)
        
        # Regex-based check for SQL and shell commands
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append(f"Dangerous pattern detected: {pattern}")
        
        if issues:
            msg = "⚠️ Safety Block: " + "; ".join(issues)
            msg += "\n\nTo execute anyway, use force=True parameter."
            return False, msg
            
        return True, "Code passed safety checks."
    
    @staticmethod
    def _get_call_name(node: ast.Call) -> str:
        """Extracts the full function name from a Call node."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            parts = []
            current = node.func
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return ".".join(reversed(parts))
        return ""
