import re
from collections import Counter

class RAGScrubber:
    def __init__(self, threshold=0.4):
        """
        threshold (float): If a line appears in >40% of pages, treat as header/footer.
        """
        self.threshold = threshold

    def _find_recurring_lines(self, pages):
        """Finds lines that repeat across many pages (potential headers/footers)."""
        line_counts = Counter()
        total_pages = len(pages)
        
        for page in pages:
            lines = page.split('\n')
            if not lines: continue
            
            check_lines = lines[:3] + lines[-3:]
            for line in check_lines:
                clean_line = line.strip()
                if len(clean_line) > 3:
                    line_counts[clean_line] += 1

        bad_lines = set()
        for line, count in line_counts.items():
            if count / total_pages >= self.threshold:
                bad_lines.add(line)
        
        return bad_lines

    def clean(self, raw_text_pages):
        """
        Input: List of strings (each string is a page)
        Output: Cleaned single string
        """
        bad_patterns = self._find_recurring_lines(raw_text_pages)
        cleaned_text = []

        print(f"Detected {len(bad_patterns)} headers/footers to remove.")

        for page in raw_text_pages:
            lines = page.split('\n')
            cleaned_page = []
            for line in lines:
                if line.strip() not in bad_patterns:
                    cleaned_page.append(line)
            
            page_text = "\n".join(cleaned_page)
            page_text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', page_text)
            cleaned_text.append(page_text)

        return "\n\n".join(cleaned_text)