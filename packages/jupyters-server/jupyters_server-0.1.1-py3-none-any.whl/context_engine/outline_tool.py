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
            snippet = cell.source[:50].replace('\n', ' ') + "..." if len(cell.source) > 50 else cell.source.replace('\n', ' ')
            outline.append(f"[{i}] {cell.cell_type.upper()}: {snippet}")
        return "\n".join(outline)
    except Exception as e:
        return f"Error reading outline: {str(e)}"
