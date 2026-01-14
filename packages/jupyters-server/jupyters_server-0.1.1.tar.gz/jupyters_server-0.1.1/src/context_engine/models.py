from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field

class CellOutput(BaseModel):
    output_type: str
    name: Optional[str] = None  # stdout/stderr for stream
    text: Optional[Union[str, List[str]]] = None
    data: Optional[Dict[str, Any]] = None
    execution_count: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    ename: Optional[str] = None
    evalue: Optional[str] = None
    traceback: Optional[List[str]] = None

class NotebookCell(BaseModel):
    cell_type: str  # code, markdown, raw
    source: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    execution_count: Optional[int] = None
    outputs: List[CellOutput] = Field(default_factory=list)
    
class NotebookStructure(BaseModel):
    cells: List[NotebookCell]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    nbformat: int
    nbformat_minor: int
