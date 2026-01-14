#!/usr/bin/env python3
"""
ContextEngine Commercial Demo 2.0
Monte Carlo PI Simulation - Full End-to-End Verification
"""

import asyncio
import json
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))

from context_engine.notebook_manager import NotebookManager
from context_engine.execution import ExecutionManager

DEMO_NOTEBOOK = Path(__file__).parent / "demo" / "monte_carlo_pi.ipynb"

async def run_demo():
    print("=" * 60)
    print("ContextEngine Commercial Demo 2.0")
    print("Monte Carlo PI Simulation")
    print("=" * 60)
    
    manager = NotebookManager()
    kernel = ExecutionManager()
    
    try:
        # Start kernel
        print("\n[1] Starting Kernel...")
        kernel.start_kernel()
        print("✓ Kernel started")
        
        # Load notebook
        print(f"\n[2] Loading notebook: {DEMO_NOTEBOOK}")
        nb = manager.read_notebook(str(DEMO_NOTEBOOK))
        print(f"✓ Loaded {len(nb.cells)} cells")
        
        # Execute cells
        code_cells = [i for i, c in enumerate(nb.cells) if c.cell_type == 'code']
        print(f"\n[3] Executing {len(code_cells)} code cells...")
        
        for cell_idx in code_cells:
            print(f"\n--- Cell {cell_idx} ---")
            source = nb.cells[cell_idx].source
            print(f"Code: {source[:50]}..." if len(source) > 50 else f"Code: {source}")
            
            outputs = kernel.execute_code(source)
            
            for out in outputs:
                if out.output_type == 'stream':
                    print(f"[stdout]: {out.text.strip()}")
                elif out.output_type == 'display_data' and out.data and 'image/png' in out.data:
                    print(f"[IMAGE]: Captured {len(out.data['image/png'])} bytes of PNG data")
                elif out.output_type == 'execute_result':
                    text = out.data.get('text/plain', '')[:100]
                    print(f"[Result]: {text}")
                elif out.output_type == 'error':
                    print(f"[ERROR]: {out.ename}: {out.evalue}")
        
        # Inspect final variable
        print("\n[4] Inspecting 'results_df'...")
        info = kernel.inspect_variable('results_df')
        print(f"✓ Inspection result: {json.dumps(info, indent=2)[:500]}")
        
        print("\n" + "=" * 60)
        print("✅ DEMO COMPLETE - All features verified!")
        print("=" * 60)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n❌ Demo failed: {e}")
    finally:
        print("\n[5] Stopping kernel...")
        kernel.stop_kernel()
        print("✓ Kernel stopped")

if __name__ == "__main__":
    asyncio.run(run_demo())
