import jupyter_client
import queue
import logging
from typing import List, Dict, Any, Optional
from context_engine.models import CellOutput

logger = logging.getLogger("context-engine")

class ExecutionManager:
    """Manages Jupyter kernels and code execution."""
    
    def __init__(self, kernel_name: str = "python3"):
        self.kernel_name = kernel_name
        self.km: Optional[jupyter_client.KernelManager] = None
        self.kc: Optional[jupyter_client.BlockingKernelClient] = None
        
    def start_kernel(self):
        """Starts a new kernel if not already running."""
        if self.km and self.km.is_alive():
            return

        logger.info(f"Starting kernel: {self.kernel_name}")
        self.km = jupyter_client.KernelManager(kernel_name=self.kernel_name)
        self.km.start_kernel()
        self.kc = self.km.client()
        self.kc.start_channels()
        try:
            self.kc.wait_for_ready(timeout=60)
            logger.info("Kernel ready")
        except RuntimeError:
            self.km.shutdown_kernel()
            self.km = None
            self.kc = None
            raise RuntimeError("Timeout waiting for kernel to start")

    def stop_kernel(self):
        """Shuts down the current kernel."""
        if self.kc:
            self.kc.stop_channels()
            self.kc = None
        if self.km:
            self.km.shutdown_kernel()
            self.km = None

    def _analyze_error(self, error_content: Dict[str, Any]) -> List[CellOutput]:
        """Analyzes an error and returns additional context (variable states)."""
        from context_engine.error_analysis import extract_variables_from_traceback
        
        traceback_list = error_content.get('traceback', [])
        # Extract potential variable names from traceback
        var_names = extract_variables_from_traceback(traceback_list)
        
        inspection_outputs = []
        if var_names:
            # Create a summary context block
            context_msg = ["\n[ContextEngine Auto-Analysis]"]
            context_msg.append(f"Detected variables in error: {', '.join(var_names)}")
            
            for var in var_names:
                # Inspect each variable
                # We reuse inspect_variable but format it concisely
                try:
                    info = self.inspect_variable(var)
                    if "error" not in info:
                        summary = f"{var} ({info.get('type')}): {info.get('str_repr')}"
                        if info.get('shape'):
                            summary += f" | shape={info.get('shape')}"
                        context_msg.append(f"  - {summary}")
                except Exception:
                    pass # Ignore inspection failures during error handling
            
            inspection_outputs.append(CellOutput(
                output_type='stream',
                name='stderr',
                text="\n".join(context_msg)
            ))
            
        return inspection_outputs

    def execute_code(self, code: str) -> List[CellOutput]:
        """Executes code and returns a list of outputs."""
        if not self.kc:
            self.start_kernel()
            
        # Flush any previous messages
        while True:
            try:
                 self.kc.get_iopub_msg(timeout=0.1)
            except queue.Empty:
                break
                
        # Execute
        msg_id = self.kc.execute(code)
        
        outputs = []
        error_context = []
        
        while True:
            try:
                msg = self.kc.get_iopub_msg(timeout=30)
                msg_type = msg['msg_type']
                content = msg['content']
                parent_id = msg['parent_header'].get('msg_id')
                
                if parent_id != msg_id:
                    continue
                    
                if msg_type == 'status':
                    if content['execution_state'] == 'idle':
                        break
                elif msg_type == 'execute_input':
                    continue
                elif msg_type == 'stream':
                    outputs.append(CellOutput(
                        output_type='stream',
                        text=content['text'],
                        name=content['name']
                    ))
                elif msg_type == 'execute_result':
                    outputs.append(CellOutput(
                        output_type='execute_result',
                        data=content['data'],
                        metadata=content['metadata'],
                        execution_count=content['execution_count']
                    ))
                elif msg_type == 'display_data':
                    outputs.append(CellOutput(
                        output_type='display_data',
                        data=content['data'],
                        metadata=content['metadata']
                    ))
                elif msg_type == 'error':
                    outputs.append(CellOutput(
                        output_type='error',
                        ename=content['ename'],
                        evalue=content['evalue'],
                        traceback=content['traceback']
                    ))
                    # Trigger Auto-Analysis
                    error_context = self._analyze_error(content)
                    
            except queue.Empty:
                logger.warning("Timeout waiting for output")
                break
        
        # Validate and Truncate outputs for Token Budgeting
        from context_engine.token_manager import TokenManager
        outputs.extend(error_context)
        return TokenManager.start_truncation_stream(outputs)

    def inspect_variable(self, var_name: str) -> Dict[str, Any]:
        """Inspects a variable in the kernel and returns its details."""
        if not self.kc:
            self.start_kernel()
            
        from context_engine.inspection_script import _context_engine_inspection_code
        
        # Inject the inspection function if not already there (could be optimized)
        # For robustness we execute the definition every time or we could check existence.
        # Let's simple inject + run.
        code = _context_engine_inspection_code.replace("{var_name}", var_name)
        
        outputs = self.execute_code(code)
        
        # Parse the output
        result = {}
        for out in outputs:
            if out.output_type == 'stream' and out.name == 'stdout':
                try:
                    import json
                    text = out.text
                    if isinstance(text, list):
                        text = "".join(text)
                    result = json.loads(text)
                except Exception as e:
                    logger.error(f"Failed to parse inspection output: {e}")
                    
        return result
