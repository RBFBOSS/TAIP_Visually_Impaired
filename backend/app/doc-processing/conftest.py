import sys
from pathlib import Path

# "doc-processing" is not a valid Python package name, so this folder is the
# import root of the service and must be on sys.path wherever pytest is run from.
sys.path.insert(0, str(Path(__file__).resolve().parent))
