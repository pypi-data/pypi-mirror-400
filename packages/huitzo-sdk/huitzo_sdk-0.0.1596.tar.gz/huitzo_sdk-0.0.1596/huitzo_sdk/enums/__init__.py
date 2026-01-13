# Copyright (c) Huitzo Inc.
# All rights reserved. Unauthorized copying, modification, or distribution prohibited.

"""Shared enumerations for plugin development."""

from .user import UserRole
from .config import ConfigScope
from .execution import ExecutionStatus

__all__ = ["UserRole", "ConfigScope", "ExecutionStatus"]
