import os
import tempfile
import unittest

from text_only_scanner.detector import is_text_file, filter_text_files
import base64


class DetectorTests(unittest.TestCase):
    def test_text_file(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write("Hello world\nThis is text.\n")
            path = f.name
        try:
            self.assertTrue(is_text_file(path))
        finally:
            os.remove(path)

    def test_binary_file(self):
        with tempfile.NamedTemporaryFile("wb", delete=False) as f:
            f.write(b"\x00\x01\x02\x03\xff\x00binary")
            path = f.name
        try:
            self.assertFalse(is_text_file(path))
        finally:
            os.remove(path)

    def test_empty_file(self):
        with tempfile.NamedTemporaryFile("wb", delete=False) as f:
            path = f.name
        try:
            self.assertTrue(is_text_file(path))
        finally:
            os.remove(path)

    def test_missing_path(self):
        self.assertFalse(is_text_file("no-such-file-hopefully-12345"))

    def test_filter_text_files(self):
        t = tempfile.NamedTemporaryFile("w", delete=False)
        t.write("ok\n")
        t.close()
        b = tempfile.NamedTemporaryFile("wb", delete=False)
        b.write(b"\x00\x01")
        b.close()
        try:
            accepted, rejected = filter_text_files([t.name, b.name])
            self.assertIn(t.name, accepted)
            self.assertIn(b.name, rejected)
        finally:
            os.remove(t.name)
            os.remove(b.name)

    def test_encrypted_like_printable(self):
        # Create printable but high-entropy data (base64 of random bytes)
        random_bytes = os.urandom(2048)
        printable = base64.b64encode(random_bytes)
        with tempfile.NamedTemporaryFile("wb", delete=False) as f:
            f.write(printable)
            path = f.name
        try:
            # Should be rejected as encrypted/unreadable despite being printable
            self.assertFalse(is_text_file(path))
        finally:
            os.remove(path)


if __name__ == "__main__":
    unittest.main()
