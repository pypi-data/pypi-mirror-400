"""Additional unit tests for utils module."""
import pytest
from unittest.mock import patch, MagicMock
from ai_git_utils.utils import beautify_diff, ALLOWED_EDITORS


@pytest.mark.unit
class TestUtilsAdditional:
    """Additional test cases for utils module."""
    
    def test_beautify_diff_with_empty_string(self):
        """Test beautify_diff with empty diff output."""
        beautify_diff("")
    
    def test_beautify_diff_with_simple_diff(self):
        """Test beautify_diff with simple diff output."""
        diff = """diff --git a/file.py b/file.py
index 1234567..abcdefg 100644
--- a/file.py
+++ b/file.py
@@ -1,1 +1,1 @@
-old line
+new line"""
        beautify_diff(diff)
    
    def test_beautify_diff_with_multiline_diff(self):
        """Test beautify_diff with multiline diff output."""
        diff = """diff --git a/file.py b/file.py
index 1234567..abcdefg 100644
--- a/file.py
+++ b/file.py
@@ -1,3 +1,3 @@
-line 1
-line 2
-line 3
+line 1 modified
+line 2 modified
+line 3 modified"""
        beautify_diff(diff)
    
    def test_beautify_diff_with_binary_file(self):
        """Test beautify_diff with binary file diff."""
        diff = """diff --git a/binary.dat b/binary.dat
index 1234567..abcdefg 100644
Binary files a/binary.dat and b/binary.dat differ"""
        beautify_diff(diff)
    
    def test_allowed_editors_list(self):
        """Test that ALLOWED_EDITORS contains expected editors."""
        assert "vim" in ALLOWED_EDITORS
        assert "vi" in ALLOWED_EDITORS
        assert "nano" in ALLOWED_EDITORS
        assert "emacs" in ALLOWED_EDITORS
        assert "code" in ALLOWED_EDITORS
        assert "subl" in ALLOWED_EDITORS