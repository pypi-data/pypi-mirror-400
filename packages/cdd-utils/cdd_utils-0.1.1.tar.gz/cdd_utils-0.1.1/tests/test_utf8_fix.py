"""Tests for cdd-utils."""

import pytest
from pathlib import Path
import tempfile

from cdd_utils.utf8_fix import (
    is_printable_ascii,
    scan_content,
    fix_content,
    classify_issues_smart,
    NORMALIZE_MAP,
)


class TestIsPrintableAscii:
    """Tests for is_printable_ascii function."""
    
    def test_printable_ascii(self):
        """Printable ASCII characters should return True."""
        for char in 'abcABC123!@# ':
            assert is_printable_ascii(char), f"'{char}' should be printable ASCII"
    
    def test_whitespace(self):
        """Tab, newline, carriage return should return True."""
        assert is_printable_ascii('\t')
        assert is_printable_ascii('\n')
        assert is_printable_ascii('\r')
    
    def test_non_ascii(self):
        """Non-ASCII characters should return False."""
        assert not is_printable_ascii('•')
        assert not is_printable_ascii('→')
        assert not is_printable_ascii('é')
        assert not is_printable_ascii('"')


class TestScanContent:
    """Tests for scan_content function."""
    
    def test_clean_content(self):
        """Clean ASCII content should return no issues."""
        content = "def hello():\n    return 'world'"
        issues = scan_content(content)
        assert len(issues) == 0
    
    def test_smart_quote(self):
        """Smart quotes should be detected."""
        content = 'text = "hello"'
        issues = scan_content(content)
        assert len(issues) == 2  # opening and closing smart quote
        assert issues[0].codepoint == 'U+201C'
        assert issues[1].codepoint == 'U+201D'
    
    def test_bullet(self):
        """Bullet character should be detected."""
        content = '• item one'
        issues = scan_content(content)
        assert len(issues) == 1
        assert issues[0].codepoint == 'U+2022'
        assert issues[0].replacement == '*'


class TestFixContent:
    """Tests for fix_content function."""
    
    def test_fix_smart_quotes(self):
        """Smart quotes should be normalized."""
        content = '"hello"'
        fixed, count = fix_content(content)
        assert fixed == '"hello"'
        assert count == 2
    
    def test_fix_em_dash(self):
        """Em dash should be normalized."""
        content = 'one—two'
        fixed, count = fix_content(content)
        assert fixed == 'one--two'
        assert count == 1
    
    def test_fix_arrow(self):
        """Arrow should be normalized."""
        content = 'a → b'
        fixed, count = fix_content(content)
        assert fixed == 'a -> b'
        assert count == 1
    
    def test_preserve_ascii(self):
        """ASCII content should be unchanged."""
        content = "def foo():\n    return 42"
        fixed, count = fix_content(content)
        assert fixed == content
        assert count == 0


class TestClassifyIssuesSmart:
    """Tests for smart classification of issues."""
    
    def test_isolated_is_legitimate(self):
        """Single isolated non-ASCII should be legitimate."""
        line = 'prefix • suffix'
        issues = scan_content(line)
        legit, susp = classify_issues_smart(line, issues)
        assert len(legit) == 1
        assert len(susp) == 0
    
    def test_clustered_is_suspicious(self):
        """Adjacent non-ASCII should be suspicious."""
        # Simulate corruption: adjacent non-ASCII characters
        line = 'text \u00e2\u2020\u2019 more'  # -> as separate chars
        issues = scan_content(line)
        legit, susp = classify_issues_smart(line, issues)
        # All clustered chars should be suspicious
        assert len(susp) >= 2
    
    def test_mixed_classification(self):
        """Line with both isolated and clustered should classify correctly."""
        # Isolated bullet, then corruption  
        line = '\u2022 item \u00e2\u2020\u2019 next'  # • item -> next
        issues = scan_content(line)
        legit, susp = classify_issues_smart(line, issues)
        # Bullet is isolated (legitimate), corruption is clustered (suspicious)
        assert len(legit) >= 1
        assert len(susp) >= 2


class TestSmartFix:
    """Tests for smart fix mode (only_suspicious=True)."""
    
    def test_preserves_isolated(self):
        """Smart fix should preserve isolated non-ASCII."""
        content = 'button = "•"'
        fixed, count = fix_content(content, only_suspicious=True)
        # Bullet is isolated, should be preserved
        assert '•' in fixed
        assert count == 0
    
    def test_fixes_clustered(self):
        """Smart fix should fix clustered non-ASCII."""
        # Two adjacent non-ASCII (suspicious)
        content = 'text ""\n'  # smart quotes are adjacent
        fixed, count = fix_content(content, only_suspicious=True)
        # Adjacent smart quotes should be fixed
        assert count == 2


class TestNormalizeMap:
    """Tests for the normalization map coverage."""
    
    def test_common_chars_mapped(self):
        """Common problematic characters should have mappings."""
        assert '"' in NORMALIZE_MAP  # left double quote
        assert '"' in NORMALIZE_MAP  # right double quote
        assert '—' in NORMALIZE_MAP  # em dash
        assert '→' in NORMALIZE_MAP  # arrow
        assert '•' in NORMALIZE_MAP  # bullet
        assert '\u00a0' in NORMALIZE_MAP  # non-breaking space
    
    def test_replacement_char_mapped(self):
        """Replacement character (corruption indicator) should be mapped."""
        assert '\ufffd' in NORMALIZE_MAP
        assert NORMALIZE_MAP['\ufffd'] == '?'
