import re
import sys
import traceback

def extract_variables_from_traceback(tb_list):
    """
    Analyzes a traceback list and returns a set of potential variable names 
    involved in the error.
    """
    variables = set()
    # Regex to find identifiers in code lines from traceback
    # Matches words that look like variables
    identifier_pattern = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")
    
    for item in tb_list:
        if isinstance(item, str):
            # It's a string line
            matches = identifier_pattern.findall(item)
            # Filter keywords or common generic words could be improved
            for m in matches:
                if len(m) > 1 and not m.startswith('_'): # Heuristic
                    variables.add(m)
    return list(variables)

# Enhanced inspection for pagination
_context_engine_slice_code = """
def _context_engine_slice(var_name, start=0, end=10):
    import json
    import pandas as pd
    try:
        if var_name not in globals():
            return json.dumps({"error": f"Variable '{var_name}' not found"})
        obj = globals()[var_name]
        
        result = {"type": type(obj).__name__}
        
        if isinstance(obj, pd.DataFrame):
            # Safe slicing
            max_rows = len(obj)
            safe_end = min(end, max_rows)
            safe_start = min(start, safe_end)
            sliced = obj.iloc[safe_start:safe_end]
            result["data"] = sliced.to_dict(orient='records')
            result["pagination"] = {"total": max_rows, "start": safe_start, "end": safe_end}
            
        elif isinstance(obj, list):
            result["data"] = obj[start:end]
            result["pagination"] = {"total": len(obj), "start": start, "end": end}
            
        else:
             result["error"] = "Variable type not supported for slicing"
             
        return json.dumps(result, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})

print(_context_engine_slice('{var_name}', {start}, {end}))
"""
