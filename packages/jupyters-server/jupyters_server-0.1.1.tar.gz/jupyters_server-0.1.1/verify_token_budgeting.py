import asyncio
import os
from context_engine.notebook_manager import NotebookManager
from context_engine.execution import ExecutionManager

async def run_token_budget_demo():
    print("=== ContextEngine Phase 3: Token Budgeting Verification ===")
    
    manager = NotebookManager()
    kernel = ExecutionManager()
    
    try:
        print("\n[1] Setup...")
        kernel.start_kernel()
        
        # 1. Test Stream Truncation
        print("\n[2] Testing Stream Truncation (Printing 100 lines)...")
        stream_code = """
for i in range(100):
    print(f"Log line {i}")
"""
        outputs = kernel.execute_code(stream_code)
        for out in outputs:
            if out.output_type == 'stream':
                print(f"Original Length (chars): {len(out.text)}")
                print("--- Output Start ---")
                print(out.text[:200])
                print("...")
                print(out.text[-200:])
                print("--- Output End ---")
                
                if "ContextEngine: Truncated" in out.text:
                    print("✓ Stream Truncation Verified!")
                else:
                    print("❌ Stream Truncation Failed!")

        # 2. Test Large Result Truncation
        print("\n[3] Testing Large Result Truncation (Large String)...")
        result_code = "'A' * 5000"
        outputs = kernel.execute_code(result_code)
        for out in outputs:
            if out.output_type == 'execute_result':
                data = out.data.get('text/plain', '')
                print(f"Original Length: {len(data)}")
                if "ContextEngine: Truncated" in data:
                    print("✓ Result Truncation Verified!")
                else:
                     print(f"❌ Result Truncation Failed! (Len: {len(data)})")
                     
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Verification failed: {e}")
    finally:
        kernel.stop_kernel()
        print("\n[4] Kernel stopped.")

if __name__ == "__main__":
    asyncio.run(run_token_budget_demo())
