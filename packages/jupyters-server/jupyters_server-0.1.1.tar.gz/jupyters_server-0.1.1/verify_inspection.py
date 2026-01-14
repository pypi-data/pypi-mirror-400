import asyncio
import os
import shutil
from context_engine.notebook_manager import NotebookManager
from context_engine.execution import ExecutionManager

async def run_inspection_demo():
    print("=== ContextEngine Step 2: Inspection Verification ===")
    
    # Setup
    test_dir = "/Users/michal/Documents/ContextEngine/demo"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    nb_path = os.path.join(test_dir, "inspection_demo.ipynb")
    
    manager = NotebookManager()
    kernel = ExecutionManager()
    
    try:
        # 1. Create Notebook
        print(f"\n[1] Creating notebook at {nb_path}...")
        import nbformat
        nb = nbformat.v4.new_notebook()
        manager.save_notebook(nb_path, nb)
        
        # 2. Add Code to create rich variables
        print("\n[2] executing setup code (Pandas/Numpy)...")
        kernel.start_kernel()
        
        setup_code = """
import pandas as pd
import numpy as np

df = pd.DataFrame({
    'A': np.random.rand(100),
    'B': np.random.randint(0, 100, 100),
    'C': ['foo', 'bar'] * 50
})
my_array = np.array([1, 2, 3, 4, 5])
        """
        kernel.execute_code(setup_code)
        print("✓ Variables 'df' and 'my_array' created.")
        
        # 3. Inspect DataFrame
        print("\n[3] Inspecting 'df'...")
        df_info = kernel.inspect_variable("df")
        print(f"✓ DF Type: {df_info.get('type')}")
        print(f"✓ DF Shape: {df_info.get('shape')}")
        print(f"✓ DF Columns: {df_info.get('columns')}")
        
        # 4. Inspect Array
        print("\n[4] Inspecting 'my_array'...")
        arr_info = kernel.inspect_variable("my_array")
        print(f"✓ Array Type: {arr_info.get('type')}")
        print(f"✓ Array Shape: {arr_info.get('shape')}")
        
        # 5. Inspect Missing Variable
        print("\n[5] Inspecting non-existent variable...")
        missing_info = kernel.inspect_variable("ghost_var")
        print(f"✓ Result: {missing_info}")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Verification failed: {e}")
    finally:
        kernel.stop_kernel()
        print("\n[6] Kernel stopped.")

if __name__ == "__main__":
    asyncio.run(run_inspection_demo())
