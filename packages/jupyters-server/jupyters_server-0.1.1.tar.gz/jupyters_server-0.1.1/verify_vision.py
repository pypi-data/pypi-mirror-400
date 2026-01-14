import asyncio
from context_engine.notebook_manager import NotebookManager
from context_engine.execution import ExecutionManager

async def run_vision_demo():
    print("=== ContextEngine Phase 4: Multimodal Vision Verification ===")
    
    manager = NotebookManager()
    kernel = ExecutionManager()
    
    try:
        print("\n[1] Starting Kernel...")
        kernel.start_kernel()
        
        # 1. Generate Plot
        print("\n[2] Generating Plot (Matplotlib)...")
        plot_code = """
import matplotlib.pyplot as plt
import numpy as np

plt.figure(figsize=(2,2))
plt.plot(np.sin(np.linspace(0, 10, 10)))
plt.show()
print("Plot generated")
"""
        outputs = kernel.execute_code(plot_code)
        
        image_found = False
        
        for out in outputs:
            if out.output_type == 'display_data' or out.output_type == 'execute_result':
                if 'image/png' in out.data:
                    print("✓ Found image/png data!")
                    print(f"  - Length: {len(out.data['image/png'])}")
                    print(f"  - Snippet: {out.data['image/png'][:50]}...")
                    image_found = True
        
        if image_found:
             print("✓ Multimodal Perception Verified: Kernel returned image data.")
        else:
             print("❌ Failed to capture image data.")
             
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Verification failed: {e}")
    finally:
        kernel.stop_kernel()
        print("\n[3] Kernel stopped.")

if __name__ == "__main__":
    asyncio.run(run_vision_demo())
