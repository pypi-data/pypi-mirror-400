import logging
import re
from typing import List, Dict, Any, Union
from context_engine.models import CellOutput

logger = logging.getLogger("context-engine")

# Patterns to collapse (regex, label)
COLLAPSE_PATTERNS = [
    (r'(Epoch \d+/\d+.*\n)', 'epoch'),
    (r'(Iteration \d+:.*\n)', 'iteration'),
    (r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\n)', 'log'),
    (r'(Step \d+:.*\n)', 'step'),
]

class TokenManager:
    """Manages token creation and budgeting by truncating large outputs."""
    
    # Constants for limits
    MAX_STREAM_LINES = 20
    MAX_TEXT_CHARS = 2000
    MAX_ERROR_TRACEBACK_LINES = 20
    
    @classmethod
    def collapse_patterns(cls, text: str) -> str:
        """Collapses repetitive patterns like epochs and iterations."""
        for pattern, label in COLLAPSE_PATTERNS:
            matches = re.findall(pattern, text)
            if len(matches) > 5:
                first, last = matches[0].strip(), matches[-1].strip()
                # Remove all matches
                text = re.sub(pattern, '', text)
                # Add collapsed summary
                collapsed = f"{first}\n... [{len(matches)-2} {label}s collapsed] ...\n{last}\n"
                text = collapsed + text
        return text
    
    @classmethod
    def truncate_output(cls, output: CellOutput) -> CellOutput:
        """Truncates a single cell output if it exceeds limits."""
        
        if output.output_type == 'stream':
            text = output.text
            if isinstance(text, list):
                text = "".join(text)
            
            # First, try pattern collapse
            text = cls.collapse_patterns(text)
            
            # Then, line truncation
            lines = text.splitlines()
            if len(lines) > cls.MAX_STREAM_LINES:
                keep = cls.MAX_STREAM_LINES // 2
                text = (
                    "\n".join(lines[:keep]) + 
                    f"\n\n... [ContextEngine: Truncated {len(lines) - cls.MAX_STREAM_LINES} lines] ...\n\n" + 
                    "\n".join(lines[-keep:])
                )
            output.text = text
                
        elif output.output_type == 'execute_result' or output.output_type == 'display_data':
            data = output.data
            if data and 'text/plain' in data:
                text = data['text/plain']
                if len(text) > cls.MAX_TEXT_CHARS:
                    output.data['text/plain'] = (
                        text[:cls.MAX_TEXT_CHARS] + 
                        f"\n... [ContextEngine: Truncated {len(text) - cls.MAX_TEXT_CHARS} chars] ..."
                    )
        
        elif output.output_type == 'error':
            traceback = output.traceback
            if traceback and len(traceback) > cls.MAX_ERROR_TRACEBACK_LINES:
                 output.traceback = (
                     traceback[:5] + 
                     [f"... [ContextEngine: Truncated {len(traceback) - 10} stack frames] ..."] + 
                     traceback[-5:]
                 )
                 
        return output

    @classmethod
    def start_truncation_stream(cls, outputs: List[CellOutput]) -> List[CellOutput]:
        """Processes a list of outputs and applies truncation."""
        return [cls.truncate_output(out) for out in outputs]

