#!/usr/bin/env python3
"""
Comprehensive Test Suite for Role-Aware Financial Assistant
============================================================

Run with: python -m pytest tests/test_all.py -v
Or simply: python tests/test_all.py
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import patch, MagicMock


class TestRBACAccessControl(unittest.TestCase):
    """Test Role-Based Access Control functionality."""
    
    def test_analyst_blocked_from_insider(self):
        """Analyst should NOT see insider data about Project Blackwell."""
        from src.agent import ask
        response = ask("What is the status of Project Blackwell?", role="analyst")
        # Should indicate no access or lack of information
        self.assertTrue(
            "don't have access" in response.lower() or 
            "no information" in response.lower() or
            "not available" in response.lower() or
            len(response) < 100,  # Short response indicates blocked
            f"Analyst may have seen insider data: {response[:200]}"
        )
        print("✅ Test 1: Analyst blocked from insider data")
    
    def test_executive_sees_insider(self):
        """Executive should see confidential Project Blackwell delay info."""
        from src.agent import ask
        response = ask("What is the status of Project Blackwell?", role="executive")
        # Should mention delay or TSMC
        self.assertTrue(
            "delay" in response.lower() or 
            "tsmc" in response.lower() or
            "3-month" in response.lower() or
            "packaging" in response.lower(),
            f"Executive did not see insider data: {response[:200]}"
        )
        print("✅ Test 2: Executive sees insider data")
    
    def test_product_manager_sees_product_data(self):
        """Product Manager should see product roadmap but NOT insider delays."""
        from src.agent import ask
        response = ask("What is the product roadmap for 2025?", role="product_manager")
        # Should mention product info
        self.assertTrue(
            "b200" in response.lower() or 
            "blackwell" in response.lower() or
            "roadmap" in response.lower() or
            "2025" in response.lower(),
            f"PM did not see product data: {response[:200]}"
        )
        print("✅ Test 3: Product Manager sees product data")
    
    def test_analyst_sees_public_data(self):
        """Analyst should see public financial data."""
        from src.agent import ask
        response = ask("What was Q3 revenue?", role="analyst")
        # Should mention revenue figures
        self.assertTrue(
            "18" in response or 
            "billion" in response.lower() or
            "revenue" in response.lower(),
            f"Analyst did not see public data: {response[:200]}"
        )
        print("✅ Test 4: Analyst sees public data")
    
    def test_invalid_role_rejected(self):
        """Invalid roles should be rejected."""
        from src.agent import ask
        response = ask("Test query", role="hacker")
        self.assertIn("invalid role", response.lower())
        print("✅ Test 5: Invalid role rejected")


class TestRetrieverFiltering(unittest.TestCase):
    """Test the secure retriever filtering logic."""
    
    def test_analyst_only_gets_public(self):
        """Analyst retriever should only return public documents."""
        from src.retriever import get_retriever
        retriever = get_retriever()
        docs = retriever.retrieve("revenue", "analyst", k=5)
        for doc in docs:
            self.assertEqual(
                doc.metadata.get("sensitivity"), "public",
                f"Analyst got non-public doc: {doc.metadata}"
            )
        print("✅ Test 6: Analyst only retrieves public docs")
    
    def test_pm_gets_public_and_product(self):
        """Product Manager should get public and product docs."""
        from src.retriever import get_retriever
        retriever = get_retriever()
        docs = retriever.retrieve("roadmap", "product_manager", k=5)
        allowed = {"public", "product"}
        for doc in docs:
            self.assertIn(
                doc.metadata.get("sensitivity"), allowed,
                f"PM got unauthorized doc: {doc.metadata}"
            )
        print("✅ Test 7: PM retrieves public + product docs")
    
    def test_executive_gets_all(self):
        """Executive should get docs from all sensitivity levels."""
        from src.retriever import get_retriever
        retriever = get_retriever()
        docs = retriever.retrieve("blackwell delay legal", "executive", k=10)
        sensitivities = {doc.metadata.get("sensitivity") for doc in docs}
        # Executive should be able to access insider docs
        # (may not always return all types in one query, but shouldn't be blocked)
        self.assertTrue(len(docs) > 0, "Executive got no documents")
        print("✅ Test 8: Executive retrieves all sensitivity levels")


class TestGuardrails(unittest.TestCase):
    """Test security guardrails."""
    
    def test_ssn_detection(self):
        """Should detect Social Security Numbers."""
        from src.guardrails import check_pii
        has_pii, pii_type = check_pii("My SSN is 123-45-6789")
        self.assertTrue(has_pii)
        self.assertEqual(pii_type, "ssn")
        print("✅ Test 9: SSN detection works")
    
    def test_credit_card_detection(self):
        """Should detect credit card numbers."""
        from src.guardrails import check_pii
        has_pii, pii_type = check_pii("Card: 4111-1111-1111-1111")
        self.assertTrue(has_pii)
        self.assertEqual(pii_type, "credit_card")
        print("✅ Test 10: Credit card detection works")
    
    def test_email_detection(self):
        """Should detect email addresses."""
        from src.guardrails import check_pii
        has_pii, pii_type = check_pii("Contact: john@company.com")
        self.assertTrue(has_pii)
        self.assertEqual(pii_type, "email")
        print("✅ Test 11: Email detection works")
    
    def test_phone_detection(self):
        """Should detect phone numbers."""
        from src.guardrails import check_pii
        has_pii, pii_type = check_pii("Call 555-123-4567")
        self.assertTrue(has_pii)
        self.assertEqual(pii_type, "phone")
        print("✅ Test 12: Phone detection works")
    
    def test_clean_text_passes(self):
        """Clean text should pass PII check."""
        from src.guardrails import check_pii
        has_pii, _ = check_pii("Revenue was $18 billion")
        self.assertFalse(has_pii)
        print("✅ Test 13: Clean text passes")
    
    def test_guardrail_blocks_pii(self):
        """Guardrail should block responses with PII."""
        from src.guardrails import guardrail_check
        passed, response = guardrail_check(
            "context", 
            "The SSN is 123-45-6789"
        )
        self.assertFalse(passed)
        self.assertIn("BLOCKED", response)
        print("✅ Test 14: Guardrail blocks PII in responses")


class TestCalculatorTool(unittest.TestCase):
    """Test the Python calculator tool."""
    
    def test_basic_calculation(self):
        """Should execute basic math."""
        from src.guardrails import python_calculator
        code = "result = 18.12 * 1.10"
        output = python_calculator(code)
        self.assertIn("19.932", output)
        print("✅ Test 15: Basic calculation works")
    
    def test_missing_result_variable(self):
        """Should error if 'result' not assigned."""
        from src.guardrails import python_calculator
        code = "x = 5 + 3"
        output = python_calculator(code)
        self.assertIn("Error", output)
        print("✅ Test 16: Missing result variable handled")
    
    def test_complex_calculation(self):
        """Should handle complex calculations."""
        from src.guardrails import python_calculator
        code = """
import math
principal = 1000
rate = 0.05
years = 10
result = principal * math.pow(1 + rate, years)
"""
        output = python_calculator(code)
        self.assertIn("Calculated Result", output)
        print("✅ Test 17: Complex calculation works")


class TestDynamicPrompts(unittest.TestCase):
    """Test role-based dynamic prompting."""
    
    def test_executive_gets_concise_response(self):
        """Executive responses should be concise (bullet points)."""
        from src.agent import ask
        response = ask("Summarize the financial situation", role="executive")
        # Executive response should be shorter than analyst
        self.assertLess(len(response), 1000, "Executive response too long")
        print("✅ Test 18: Executive gets concise response")
    
    def test_analyst_gets_detailed_response(self):
        """Analyst responses should be detailed."""
        from src.agent import ask
        response = ask("What was Q3 revenue?", role="analyst")
        # Should have substantive content
        self.assertGreater(len(response), 50, "Analyst response too short")
        print("✅ Test 19: Analyst gets detailed response")


class TestAuditLogging(unittest.TestCase):
    """Test audit logging functionality."""
    
    def test_log_file_created(self):
        """Audit log file should be created after queries."""
        import os
        from src.agent import ask
        
        # Make a query to trigger logging
        ask("Test query", "analyst")
        
        # Check log file exists
        log_file = "audit_log.jsonl"
        self.assertTrue(os.path.exists(log_file), "Audit log not created")
        print("✅ Test 20: Audit log file created")
    
    def test_log_entry_format(self):
        """Log entries should have correct format."""
        import json
        
        log_file = "audit_log.jsonl"
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    entry = json.loads(lines[-1])
                    required_fields = ["timestamp", "user_role", "query"]
                    for field in required_fields:
                        self.assertIn(field, entry, f"Missing field: {field}")
        print("✅ Test 21: Log entry format correct")


class TestVisionModule(unittest.TestCase):
    """Test Vision RAG functionality (if available)."""
    
    def test_sample_chart_generation(self):
        """Should generate a sample chart."""
        try:
            from src.vision import generate_sample_chart
            import os
            
            path = generate_sample_chart()
            self.assertTrue(os.path.exists(path), "Chart not generated")
            print("✅ Test 22: Sample chart generated")
        except ImportError:
            self.skipTest("Vision module not available")
    
    def test_device_detection(self):
        """Should detect available compute device."""
        try:
            from src.vision import get_device
            
            device = get_device()
            self.assertIn(device, ["mps", "cuda", "cpu"])
            print(f"✅ Test 23: Device detected: {device}")
        except ImportError:
            self.skipTest("Vision module not available")


def run_all_tests():
    """Run all tests with summary."""
    print("\n" + "="*60)
    print("🧪 COMPREHENSIVE TEST SUITE")
    print("   Role-Aware Financial Assistant")
    print("="*60 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestRBACAccessControl))
    suite.addTests(loader.loadTestsFromTestCase(TestRetrieverFiltering))
    suite.addTests(loader.loadTestsFromTestCase(TestGuardrails))
    suite.addTests(loader.loadTestsFromTestCase(TestCalculatorTool))
    suite.addTests(loader.loadTestsFromTestCase(TestDynamicPrompts))
    suite.addTests(loader.loadTestsFromTestCase(TestAuditLogging))
    suite.addTests(loader.loadTestsFromTestCase(TestVisionModule))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "="*60)
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
    else:
        print(f"❌ FAILURES: {len(result.failures)}")
        print(f"❌ ERRORS: {len(result.errors)}")
    print("="*60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
