import io
import sys
import unittest
from contextlib import redirect_stdout
from importlib.metadata import PackageNotFoundError
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import common.arguments as arguments


class ResolveVersionTests(unittest.TestCase):
    def test_version_argument_falls_back_when_metadata_missing(self) -> None:
        with patch("common.arguments.get_version", side_effect=PackageNotFoundError("quick-assistant")):
            parser = arguments.create_parser()
            with redirect_stdout(io.StringIO()):
                with self.assertRaises(SystemExit) as context:
                    parser.parse_args(["--version"])

        self.assertEqual(context.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
