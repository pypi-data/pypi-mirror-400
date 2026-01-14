import asyncio
import os
import shutil
from context_engine.notebook_manager import NotebookManager
from context_engine.execution import ExecutionManager

async def run_analysis_demo():
    print("=== ContextEngine Step 3: Error Analysis & Deep Dive Verification ===")
    
    manager = NotebookManager()
    kernel = ExecutionManager()
    
    try:
        # 1. Setup Data
        print("\n[1] Setting up data...")
        kernel.start_kernel()
        setup_code = """
import pandas as pd
df = pd.DataFrame({'id': range(100), 'val': range(100)})
"""
        kernel.execute_code(setup_code)
        print("✓ Data frame 'df' created.")
        
        # 2. Trigger Error (Auto-Context Test)
        print("\n[2] Triggering Error (KeyError)...")
        error_code = "print(df['non_existent_column'])"
        outputs = kernel.execute_code(error_code)
        
        error_found = False
        context_found = False
        
        for out in outputs:
            if out.output_type == 'error':
                print(f"✓ Capture Error: {out.ename}")
                error_found = True
            if out.output_type == 'stream' and '[ContextEngine Auto-Analysis]' in str(out.text):
                print("✓ Found Auto-Analysis Context:")
                print(out.text)
                context_found = True
                
        if not error_found:
            print("❌ Failed to capture error.")
        if not context_found:
            print("❌ Failed to inject auto-context.")
            
        # 3. Deep Dive Slicing
        print("\n[3] Testing Deep Dive Slicing for 'df' (rows 10-15)...")
        from context_engine.error_analysis import _context_engine_slice_code
        slice_code = _context_engine_slice_code.replace("{var_name}", "df") \
                                               .replace("{start}", "10") \
                                               .replace("{end}", "15")
        
        slice_outputs = kernel.execute_code(slice_code)
        for out in slice_outputs:
            if out.output_type == 'stream' and out.name == 'stdout':
                import json
                res = json.loads(out.text if isinstance(out.text, str) else "".join(out.text))
                print(f"✓ Sliced Data: {json.dumps(res.get('data'), indent=2)}")
                print(f"✓ Pagination: {res.get('pagination')}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Verification failed: {e}")
    finally:
        kernel.stop_kernel()
        print("\n[4] Kernel stopped.")

if __name__ == "__main__":
    asyncio.run(run_analysis_demo())
