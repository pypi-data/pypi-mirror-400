import unittest
import os
import vtx_protocol

class TestProtocolIntegrity(unittest.TestCase):
    def test_wit_path_resolution(self):
        path = vtx_protocol.get_wit_path()

        if not os.path.exists(path):
            self.fail(f"Critical: WIT file path resolution failed. Path not found: {path}")

        self.assertTrue(os.path.isfile(path), f"Path exists but is not a file: {path}")

    def test_wit_content_validity(self):
        path = vtx_protocol.get_wit_path()

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except IOError as e:
            self.fail(f"Failed to open WIT file for reading: {e}")

        self.assertIn(
            "package vtx:api",
            content,
            "WIT file content missing required package signature."
        )

if __name__ == '__main__':
    unittest.main()
