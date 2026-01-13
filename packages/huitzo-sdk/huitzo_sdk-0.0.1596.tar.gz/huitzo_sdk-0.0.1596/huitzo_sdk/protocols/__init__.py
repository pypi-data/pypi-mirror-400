# Copyright (c) Huitzo Inc.
# All rights reserved. Unauthorized copying, modification, or distribution prohibited.

"""Protocol definitions for plugin development."""

from .command import CommandContext, CommandProtocol, CommandResult

__all__ = ["CommandProtocol", "CommandContext", "CommandResult"]
