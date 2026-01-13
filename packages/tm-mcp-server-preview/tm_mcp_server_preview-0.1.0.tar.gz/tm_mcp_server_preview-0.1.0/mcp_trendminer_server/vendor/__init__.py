"""
Vendored dependencies for mcp-trendminer-server.

This directory contains bundled copies of dependencies that are not available on PyPI.
"""

# Make vendored packages importable
import sys
from pathlib import Path

# Add vendor directory to path so trendminer_interface and confighub_interface
# can be imported as if they were installed packages
vendor_dir = Path(__file__).parent
if str(vendor_dir) not in sys.path:
    sys.path.insert(0, str(vendor_dir))
