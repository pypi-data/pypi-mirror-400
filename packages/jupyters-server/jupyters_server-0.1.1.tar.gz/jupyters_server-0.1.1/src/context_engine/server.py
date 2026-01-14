import asyncio
import logging
import os
from typing import Dict
from mcp.server.fastmcp import FastMCP
from context_engine.notebook_manager import NotebookManager
from context_engine.execution import ExecutionManager
from context_engine.license import LicenseManager, check_license, check_execution_limit, record_execution
import nbformat

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("context-engine")

# Initialize Server and Manager
mcp = FastMCP("context-engine")
manager = NotebookManager()
kernels: Dict[str, ExecutionManager] = {}

def get_kernel(path: str) -> ExecutionManager:
    """Gets or creates a kernel for the given notebook path."""
    if path not in kernels:
        kernels[path] = ExecutionManager()
    return kernels[path]

@mcp.tool()
def activate_license(key: str) -> str:
    """Activates a ContextEngine license key.
    
    Args:
        key: The license key (e.g. CE-PRO-XXXX)
    """
    success, msg = LicenseManager.instance().activate_license(key)
    return msg

@mcp.tool()
def get_server_info() -> str:
    """Returns information about the ContextEngine server."""
    return "ContextEngine MCP Server v0.1.0 - Commercial Grade Jupyter Integration"

@mcp.tool()
def read_notebook(path: str) -> str:
    """Reads a notebook and returns its content as a JSON string.
    
    Args:
        path: Absolute path to the .ipynb file
    """
    try:
        nb = manager.read_notebook(path)
        return nbformat.writes(nb)
    except Exception as e:
        return f"Error reading notebook: {str(e)}"

@mcp.tool()
def read_cell(path: str, index: int) -> str:
    """Reads the source code of a specific cell.
    
    Args:
        path: Absolute path to the .ipynb file
        index: Zero-based index of the cell
    """
    try:
        return manager.get_cell_source(path, index)
    except Exception as e:
        return f"Error reading cell: {str(e)}"

@mcp.tool()
def update_cell(path: str, index: int, new_source: str) -> str:
    """Updates the source code of a specific cell.
    
    Args:
        path: Absolute path to the .ipynb file
        index: Zero-based index of the cell
        new_source: New content for the cell
    """
    try:
        manager.update_cell_source(path, index, new_source)
        return f"Successfully updated cell {index} in {path}"
    except Exception as e:
        return f"Error updating cell: {str(e)}"

@mcp.tool()
def create_notebook(path: str) -> str:
    """Creates a new empty notebook.
    
    Args:
        path: Absolute path for the new .ipynb file
    """
    try:
        if os.path.exists(path):
            return f"Error: File already exists at {path}"
            
        nb = nbformat.v4.new_notebook()
        manager.save_notebook(path, nb)
        return f"Successfully created notebook at {path}"
    except Exception as e:
        return f"Error creating notebook: {str(e)}"

@mcp.tool()
def add_cell(path: str, source: str, cell_type: str = "code", index: int = -1) -> str:
    """Adds a new cell to the notebook.
    
    Args:
        path: Absolute path to the .ipynb file
        source: Content of the new cell
        cell_type: "code" or "markdown"
        index: Insertion index (-1 to append to end)
    """
    try:
        nb = manager.read_notebook(path)
        
        if cell_type == "code":
            new_cell = nbformat.v4.new_code_cell(source)
        elif cell_type == "markdown":
            new_cell = nbformat.v4.new_markdown_cell(source)
        else:
            return "Error: cell_type must be 'code' or 'markdown'"
            
        if index < 0 or index >= len(nb.cells):
            nb.cells.append(new_cell)
            inserted_at = len(nb.cells) - 1
        else:
            nb.cells.insert(index, new_cell)
            inserted_at = index
            
        manager.save_notebook(path, nb)
        return f"Successfully added {cell_type} cell at index {inserted_at}"
    except Exception as e:
        return f"Error adding cell: {str(e)}"

@mcp.tool()
def run_cell(path: str, index: int, force: bool = False) -> str:
    """Executes a cell in the notebook, updates outputs, and returns summary.
    
    Args:
        path: Absolute path to the .ipynb file
        index: Zero-based index of the cell
        force: If True, skip safety checks (use with caution)
    """
    try:
        # 0. License Check
        allowed, msg = check_execution_limit()
        if not allowed:
            return msg
            
        # 1. Get code
        source = manager.get_cell_source(path, index)
        
        # 2. Safety Check
        from context_engine.safety import SafetyChecker
        is_safe, msg = SafetyChecker.check_code(source, force=force)
        if not is_safe:
            return msg
        
        # 3. Get kernel
        kernel = get_kernel(path)
        
        # 4. Execute
        outputs = kernel.execute_code(source)
        
        # 5. Save outputs
        manager.update_cell_outputs(path, index, outputs)
        
        # 5b. Record Usage
        record_execution()
        
        # 6. Summarize
        summary = []
        for out in outputs:
            if out.output_type == 'stream':
                summary.append(f"[{out.name}]: {out.text}")
            elif out.output_type == 'execute_result' or out.output_type == 'display_data':
                # Handle Images
                if out.data and 'image/png' in out.data:
                    from context_engine.license import can_use_feature
                    if can_use_feature("vision"):
                        base64_img = out.data['image/png']
                        summary.append(f"![Plot](data:image/png;base64,{base64_img})")
                    else:
                        summary.append("[Plot hidden: Vision is a Pro feature]")
                
                # Handle Text
                if out.data and 'text/plain' in out.data:
                     summary.append(f"[Result]: {str(out.data.get('text/plain', ''))}")
                else:
                    summary.append("[Result/Display Data]")
            elif out.output_type == 'error':
                summary.append(f"[Error]: {out.ename}: {out.evalue}")
                
        return "\n".join(summary) if summary else "Cell executed successfully (no output)"
        
    except Exception as e:
        return f"Error executing cell: {str(e)}"

@mcp.tool()
def restart_kernel(path: str) -> str:
    """Restarts the kernel for the notebook.
    
    Args:
        path: Absolute path to the .ipynb file
    """
    try:
        if path in kernels:
            kernels[path].stop_kernel()
            del kernels[path]
        
        # Start new one
        get_kernel(path).start_kernel()
        return f"Kernel restarted for {path}"
    except Exception as e:
        return f"Error restarting kernel: {str(e)}"

@mcp.tool()
def read_notebook_outline(path: str) -> str:
    """Returns a simplified outline of the notebook (cells types and snippets).
    
    Args:
        path: Absolute path to the .ipynb file
    """
    try:
        nb = manager.read_notebook(path)
        outline = [f"Notebook: {path}"]
        outline.append(f"Cells: {len(nb.cells)}")
        for i, cell in enumerate(nb.cells):
            exec_count = f" [{cell.get('execution_count', ' ')}]" if cell.get('cell_type') == 'code' else ""
            snippet = cell.source[:50].replace('\n', ' ') + "..." if len(cell.source) > 50 else cell.source.replace('\n', ' ')
            outline.append(f"[{i}]{exec_count} {cell.cell_type.upper()}: {snippet}")
        return "\n".join(outline)
    except Exception as e:
        return f"Error reading outline: {str(e)}"

@mcp.tool()
def inspect_variable(path: str, var_name: str) -> str:
    """Inspects a variable in the notebook's active kernel.
    
    Returns semantic details like DataFrame head/schema, Tensor shapes, etc.
    
    Args:
        path: Absolute path to the .ipynb file
        var_name: Name of the variable to inspect (e.g. 'df', 'model')
    """
    from context_engine.license import can_use_feature
    
    if not can_use_feature("inspect_variable"):
        return "Error: specific variable inspection is a Pro feature. Upgrade at contextengine.dev"
        
    try:
        kernel = get_kernel(path)
        result = kernel.inspect_variable(var_name)
        
        # Format the output for the LLM
        import json
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error inspecting variable: {str(e)}"

@mcp.tool()
def read_variable_sample(path: str, var_name: str, start: int = 0, end: int = 10) -> str:
    """Reads a slice of a variable (DataFrame rows, List items) for deep dive.
    
    Args:
        path: Absolute path to the .ipynb file
        var_name: Name of the variable
        start: Start index (default 0)
        end: End index (default 10)
    """
    try:
        kernel = get_kernel(path)
        # We need to implement manual code execution for slicing using our helper script
        from context_engine.error_analysis import _context_engine_slice_code
        
        code = _context_engine_slice_code.replace("{var_name}", var_name) \
                                         .replace("{start}", str(start)) \
                                         .replace("{end}", str(end))
                                         
        outputs = kernel.execute_code(code)
        
        # Parse return
        for out in outputs:
            if out.output_type == 'stream' and out.name == 'stdout':
                 import json
                 text = out.text
                 if isinstance(text, list):
                     text = "".join(text)
                 return text # Already JSON
                 
        return json.dumps({"error": "No output from slicing"})
    except Exception as e:
        return f"Error reading variable sample: {str(e)}"

@mcp.tool()
def get_execution_order(path: str) -> str:
    """Returns cells sorted by execution order (logical flow).
    
    Helps understand the actual state of the notebook based on when cells were run.
    
    Args:
        path: Absolute path to the .ipynb file
    """
    try:
        nb = manager.read_notebook(path)
        
        # Collect executed cells with their counts
        executed = []
        for i, cell in enumerate(nb.cells):
            if cell.get('cell_type') == 'code' and cell.get('execution_count'):
                executed.append({
                    'index': i,
                    'execution_count': cell['execution_count'],
                    'snippet': cell.source[:50].replace('\n', ' ') + "..." if len(cell.source) > 50 else cell.source.replace('\n', ' ')
                })
        
        # Sort by execution count
        executed.sort(key=lambda x: x['execution_count'])
        
        # Format output
        lines = [f"Execution Order for {path}:"]
        for item in executed:
            lines.append(f"[Step {item['execution_count']}] Cell {item['index']}: {item['snippet']}")
            
        if not executed:
            lines.append("No cells have been executed yet.")
            
        return "\n".join(lines)
    except Exception as e:
        return f"Error getting execution order: {str(e)}"

@mcp.tool()
def set_profile(profiles: str) -> str:
    """Activates domain profiles for enhanced variable inspection.
    
    Profiles provide specialized inspection for domain-specific objects.
    
    Args:
        profiles: Comma-separated list of profiles: 'base', 'ml', 'finance', or 'all'
    """
    from context_engine.profiles import set_profiles
    from context_engine.license import can_use_feature
    
    if not can_use_feature("domain_profiles"):
        return "Error: Domain profiles are a Team feature. Upgrade to Team plan."
    
    profile_list = [p.strip().lower() for p in profiles.split(',')]
    
    if 'all' in profile_list:
        profile_list = ['base', 'ml', 'finance']
    
    valid = {'base', 'ml', 'finance'}
    invalid = set(profile_list) - valid
    if invalid:
        return f"Error: Invalid profiles: {invalid}. Valid options: base, ml, finance, all"
    
    set_profiles(profile_list)
    return f"Active profiles set to: {profile_list}"

@mcp.tool()
def split_cell(path: str, index: int, line: int) -> str:
    """Splits a cell at the specified line number.
    
    Args:
        path: Absolute path to the .ipynb file
        index: Zero-based index of the cell to split
        line: Line number to split at (1-indexed, content before this line stays in first cell)
    """
    try:
        nb = manager.read_notebook(path)
        
        if index < 0 or index >= len(nb.cells):
            return f"Error: Cell index {index} out of range"
            
        cell = nb.cells[index]
        lines = cell.source.split('\n')
        
        if line < 1 or line > len(lines):
            return f"Error: Line {line} out of range (1-{len(lines)})"
            
        # Split content
        first_part = '\n'.join(lines[:line])
        second_part = '\n'.join(lines[line:])
        
        # Update original cell
        cell.source = first_part
        
        # Create new cell (same type)
        if cell.cell_type == 'code':
            new_cell = nbformat.v4.new_code_cell(second_part)
        else:
            new_cell = nbformat.v4.new_markdown_cell(second_part)
            
        # Insert after current
        nb.cells.insert(index + 1, new_cell)
        manager.save_notebook(path, nb)
        
        return f"Split cell {index} at line {line}. New cell created at index {index + 1}"
    except Exception as e:
        return f"Error splitting cell: {str(e)}"

@mcp.tool()
def merge_cells(path: str, start: int, end: int) -> str:
    """Merges multiple cells into one.
    
    Args:
        path: Absolute path to the .ipynb file
        start: Index of first cell to merge
        end: Index of last cell to merge (inclusive)
    """
    try:
        nb = manager.read_notebook(path)
        
        if start < 0 or end >= len(nb.cells) or start > end:
            return f"Error: Invalid range {start}-{end}"
            
        # Collect content
        merged_source = '\n\n'.join(nb.cells[i].source for i in range(start, end + 1))
        
        # Use type of first cell
        first_cell = nb.cells[start]
        first_cell.source = merged_source
        
        # Remove merged cells (in reverse to maintain indices)
        for i in range(end, start, -1):
            nb.cells.pop(i)
            
        manager.save_notebook(path, nb)
        
        return f"Merged cells {start} to {end} into cell {start}"
    except Exception as e:
        return f"Error merging cells: {str(e)}"


def main():
    """Entry point for the MCP server."""
    import sys
    logger.info("Starting Jupyters MCP Server...")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"MCP Server ready to accept connections")
    mcp.run()


if __name__ == "__main__":
    main()

