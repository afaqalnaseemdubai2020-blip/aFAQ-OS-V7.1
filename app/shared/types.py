"""
Shared type aliases used across all modules.
"""

from typing import NewType
from datetime import datetime

ID = NewType("ID", str)
Timestamp = datetime
ModuleName = NewType("ModuleName", str)