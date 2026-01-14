    def update_cell_outputs(self, path: str, index: int, outputs: List[Dict[str, Any]]) -> None:
        """Updates outputs of a specific cell."""
        nb = self.read_notebook(path)
        if index < 0 or index >= len(nb.cells):
            raise IndexError(f"Cell index {index} out of range (0-{len(nb.cells)-1})")
            
        # Convert Pydantic models to dict if necessary, or assume dicts
        # nbformat expects dicts (NotebookNode)
        clean_outputs = []
        for out in outputs:
            if hasattr(out, 'model_dump'):
                clean_outputs.append(out.model_dump(exclude_none=True))
            elif isinstance(out, dict):
                clean_outputs.append(out)
            else:
                clean_outputs.append(out) # Hope it's compatible
                
        nb.cells[index].outputs = clean_outputs
        self.save_notebook(path, nb)
