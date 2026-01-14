import nbformat
import os
import json
from context_engine.models import NotebookStructure, NotebookCell
from typing import Optional, List, Dict, Any

class NotebookManager:
    """Manages reading and writing of Jupyter notebooks using nbformat."""
    
    def read_notebook(self, path: str) -> nbformat.NotebookNode:
        """Reads a notebook from disk validation."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Notebook not found: {path}")
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return nbformat.read(f, as_version=4)
        except Exception as e:
            raise ValueError(f"Failed to read notebook {path}: {str(e)}")

    def save_notebook(self, path: str, notebook: nbformat.NotebookNode) -> None:
        """Atomically saves a notebook to disk."""
        temp_path = None
        try:
            # Validate before writing
            nbformat.validate(notebook)
            
            # Write to temporary file first
            dir_name = os.path.dirname(os.path.abspath(path))
            temp_path = os.path.join(dir_name, f".{os.path.basename(path)}.tmp")
            
            with open(temp_path, 'w', encoding='utf-8') as f:
                nbformat.write(notebook, f)
                
            # Rename to target (atomic on POSIX)
            os.rename(temp_path, path)
        except Exception as e:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            raise IOError(f"Failed to save notebook {path}: {str(e)}")

    def get_cell_source(self, path: str, index: int) -> str:
        """Reads source of a specific cell."""
        nb = self.read_notebook(path)
        if index < 0 or index >= len(nb.cells):
            raise IndexError(f"Cell index {index} out of range (0-{len(nb.cells)-1})")
        return nb.cells[index].source

    def update_cell_source(self, path: str, index: int, new_source: str) -> None:
        """Updates source of a specific cell."""
        nb = self.read_notebook(path)
        if index < 0 or index >= len(nb.cells):
            raise IndexError(f"Cell index {index} out of range (0-{len(nb.cells)-1})")
            
        nb.cells[index].source = new_source
        self.save_notebook(path, nb)

    def update_cell_outputs(self, path: str, index: int, outputs: List[Any]) -> None:
        """Updates outputs of a specific cell."""
        nb = self.read_notebook(path)
        if index < 0 or index >= len(nb.cells):
            raise IndexError(f"Cell index {index} out of range (0-{len(nb.cells)-1})")
            
        # Convert Pydantic models to dict if necessary
        clean_outputs = []
        for out in outputs:
            o_dict = {}
            if hasattr(out, 'model_dump'):
                o_dict = out.model_dump(exclude_none=True)
            elif hasattr(out, 'dict'):
                o_dict = out.dict(exclude_none=True)
            elif isinstance(out, dict):
                o_dict = out
            else:
                continue

            # Sanitize for nbformat compliance
            if o_dict.get('output_type') == 'stream':
                o_dict.pop('metadata', None)
                
            clean_outputs.append(nbformat.from_dict(o_dict))
                
        nb.cells[index].outputs = clean_outputs
        self.save_notebook(path, nb)
