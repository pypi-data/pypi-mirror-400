import os
import sys

# Add repo root so local package imports work when running from source
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)

from apr_detector.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
