import unittest
from rag_scrubber.cleaner import RAGScrubber

class TestRAGScrubber(unittest.TestCase):

    def setUp(self):
        self.scrubber = RAGScrubber(threshold=0.5)

    def test_header_removal(self):
        """Test if repeating headers are removed correctly."""
        dirty_pages = [
            "CONFIDENTIAL REPORT\nMarket is up.",
            "CONFIDENTIAL REPORT\nSales are good.",
            "CONFIDENTIAL REPORT\nEnd of page."
        ]
        # We expect the header to be gone
        # Note: clean() joins pages with \n\n
        expected_output = "Market is up.\n\nSales are good.\n\nEnd of page."
        result = self.scrubber.clean(dirty_pages)
        
        self.assertNotIn("CONFIDENTIAL REPORT", result)
        self.assertEqual(result.strip(), expected_output)

    def test_hyphen_fix(self):
        """Test if split words like 'per- formed' are joined."""
        pages = ["The task was per-\nformed yesterday."]
        result = self.scrubber.clean(pages)
        
        self.assertIn("performed", result)
        self.assertNotIn("per-", result)

    def test_single_page_regex(self):
        """Test if single-page junk is removed using Regex fallback."""
        # This is a SINGLE page. Stats won't work, but Regex MUST work.
        page = ["Page 1\nThis is real content.\nCopyright 2024"]
        
        result = self.scrubber.clean(page)
        
        self.assertNotIn("Page 1", result)
        self.assertNotIn("Copyright 2024", result)
        self.assertIn("This is real content", result)

    def test_threshold_logic(self):
        """Test if unique lines are PRESERVED (not deleted)."""
        pages = [
            "Unique Title 1\nContent A",
            "Unique Title 2\nContent B",
            "Unique Title 3\nContent C"
        ]
        result = self.scrubber.clean(pages)
        self.assertIn("Unique Title 1", result)

if __name__ == '__main__':
    unittest.main()