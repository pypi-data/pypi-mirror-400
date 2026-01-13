import re
from collections import Counter

class RAGScrubber:
    def __init__(self, threshold=0.4, use_regex_fallback=True):
        """
        threshold: If a line appears in >40% of pages, delete it.
        use_regex_fallback: Also use Regex to remove common junk (Page #, Confidential) on ANY page.
        """
        self.threshold = threshold
        self.use_regex_fallback = use_regex_fallback
        
        self.junk_patterns = [
            r'^\s*Page\s+\d+',
            r'^\s*\d+\s+of\s+\d+\s*$',
            r'^\s*Copyright\s+.*',
            r'^\s*All rights reserved.*',
            r'^\s*CONFIDENTIAL\s*$',
            r'^\s*https?://\S+\s*$'
        ]

    def _find_recurring_lines(self, pages):
        """Statistical Method: Finds lines that repeat across multiple pages."""
        if len(pages) < 2:
            return set()

        line_counts = Counter()
        total_pages = len(pages)
        
        for page in pages:
            lines = page.split('\n')
            if not lines: continue
            
            candidates = set(lines[:3] + lines[-3:])
            
            for line in candidates:
                clean_line = line.strip()
                if len(clean_line) > 3:
                    line_counts[clean_line] += 1

        bad_lines = set()
        for line, count in line_counts.items():
            if count / total_pages >= self.threshold:
                bad_lines.add(line)
        
        return bad_lines

    def _is_regex_junk(self, line):
        """Regex Method: Checks if a line matches common garbage patterns."""
        if not self.use_regex_fallback:
            return False
        for pattern in self.junk_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False

    def clean(self, raw_text_pages):
        bad_statistical_patterns = self._find_recurring_lines(raw_text_pages)
        
        
        cleaned_text = []

        for page in raw_text_pages:
            lines = page.split('\n')
            cleaned_page = []
            
            for line in lines:
                stripped_line = line.strip()
                
                if stripped_line in bad_statistical_patterns:
                    continue
                
                if self._is_regex_junk(stripped_line):
                    continue

                cleaned_page.append(line)
            
            page_text = "\n".join(cleaned_page)
            page_text = self.fix_hyphenation(page_text)
            cleaned_text.append(page_text)

        return "\n\n".join(cleaned_text)

    def fix_hyphenation(self, text):
        pattern = r'(\w+)-\s+([a-z]\w*)'
        return re.sub(pattern, r'\1\2', text)