import asyncio
import os
import shutil
from context_engine.notebook_manager import NotebookManager
from context_engine.execution import ExecutionManager

async def run_demo():
    print("=== ContextEngine Commercial Demo Verification ===")
    
    # Setup
    test_dir = "/Users/michal/Documents/ContextEngine/demo"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    nb_path = os.path.join(test_dir, "demo_notebook.ipynb")
    if os.path.exists(nb_path):
        os.remove(nb_path)
        
    manager = NotebookManager()
    kernel = ExecutionManager()
    
    # 1. Create Notebook
    print(f"\n[1] Creating notebook at {nb_path}...")
    import nbformat
    nb = nbformat.v4.new_notebook()
    manager.save_notebook(nb_path, nb)
    print("✓ Notebook created.")
    
    # 2. Add Code Cell
    print("\n[2] Adding code cell...")
    code = "import math\nprint(f'Math pi is: {math.pi}')\nx = 10\nx * 2"
    cell = nbformat.v4.new_code_cell(code)
    nb.cells.append(cell)
    manager.save_notebook(nb_path, nb)
    print("✓ Cell added.")
    
    # 3. Execute Cell (Simulating 'Pro' feature)
    print("\n[3] Executing cell (Live Kernel)...")
    try:
        kernel.start_kernel()
        print("✓ Kernel started.")
        
        outputs = kernel.execute_code(code)
        print(f"✓ Execution complete. captured {len(outputs)} outputs.")
        
        for out in outputs:
            if out.output_type == 'stream':
                print(f"  -> stdout: {out.text}")
            elif out.output_type == 'execute_result':
                print(f"  -> result: {out.data.get('text/plain')}")
                
        # 4. Update Notebook with Outputs
        print("\n[4] Saving outputs to file...")
        manager.update_cell_outputs(nb_path, 0, outputs)
        print("✓ Notebook saved with outputs.")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Execution failed: {e}")
    finally:
        kernel.stop_kernel()
        print("\n[5] Kernel stopped.")
        
    print("\n=== Demo Complete ===")

if __name__ == "__main__":
    asyncio.run(run_demo())
