import unittest
from context_engine.models import CellOutput
from context_engine.token_manager import TokenManager

class TestTokenManager(unittest.TestCase):
    def test_stream_truncation(self):
        # Create 100 lines
        text = "\n".join([f"Line {i}" for i in range(100)])
        out = CellOutput(output_type='stream', name='stdout', text=text)
        
        truncated = TokenManager.truncate_output(out)
        self.assertIn("ContextEngine: Truncated", truncated.text)
        self.assertTrue(truncated.text.startswith("Line 0"))
        self.assertTrue(truncated.text.endswith("Line 99"))
        print("✓ Stream Truncation Logic verified")

    def test_text_truncation(self):
        # Create 5000 chars
        text = "A" * 5000
        out = CellOutput(
            output_type='execute_result',
            data={'text/plain': text},
            execution_count=1,
            metadata={}
        )
        
        truncated = TokenManager.truncate_output(out)
        self.assertIn("ContextEngine: Truncated", truncated.data['text/plain'])
        self.assertLess(len(truncated.data['text/plain']), 3000)
        print("✓ Text Truncation Logic verified")

if __name__ == '__main__':
    unittest.main()
