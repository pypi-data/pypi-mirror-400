import unittest
import tempfile
import shutil
from pathlib import Path
from init_python_package.main import run_initializer

class TestInitializer(unittest.TestCase):
    def test_initializer_creates_structure(self):
        tmpdir = tempfile.mkdtemp()
        try:
            target = Path(tmpdir) / "my_test_package"
            run_initializer(target)

            # Assert key files exist
            self.assertTrue((target / "README.md").exists())
            self.assertTrue((target / "LICENSE").exists())
            self.assertTrue((target / "pyproject.toml").exists())
        finally:
            shutil.rmtree(tmpdir)

